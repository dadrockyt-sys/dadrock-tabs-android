#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, math, os, random, struct, subprocess, sys, time
from collections import defaultdict
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'tabcnn_runtime'))
from preprocessing import extract_cqt_features, rms_normalize, SAMPLE_RATE_HZ, HOP_LENGTH_SAMPLES

SEED=20260921
BATCH_SIZE=32
MAX_ITERATIONS=2500
CHECKPOINT_EVERY=50
FRAME_CONTEXT=9
HALF_CONTEXT=4
NUM_STRINGS=6
NUM_CLASSES=21
MASK=-100
STRING_ORDER=['E','A','D','G','B','e']
OPEN_MIDI={'E':40,'A':45,'D':50,'G':55,'B':59,'e':64}
CANON=set(STRING_ORDER)
ONSET_TOLERANCE=0.050

def read_vlq(data,i):
    v=0
    for _ in range(4):
        if i>=len(data): raise ValueError('truncated vlq')
        b=data[i];i+=1;v=(v<<7)|(b&0x7f)
        if not b&0x80:return v,i
    return v,i

def parse_track(chunk):
    i=tick=0;running=None;name=None;tempos=[];events=[];last_tick=0
    while i<len(chunk):
        delta,i=read_vlq(chunk,i);tick+=delta;last_tick=max(last_tick,tick)
        if i>=len(chunk):break
        status=chunk[i]
        if status<0x80:
            if running is None: raise ValueError('running status without status')
            status=running
        else:
            i+=1
            if status<0xf0: running=status
        if status==0xff:
            if i>=len(chunk): raise ValueError('truncated meta')
            typ=chunk[i];i+=1;n,i=read_vlq(chunk,i);payload=chunk[i:i+n];i+=n
            if len(payload)!=n: raise ValueError('truncated meta payload')
            if typ==0x03:name=payload.decode('utf-8','replace')
            elif typ==0x51 and n==3:tempos.append((tick,int.from_bytes(payload,'big')))
            continue
        if status in (0xf0,0xf7):
            n,i=read_vlq(chunk,i);i+=n;continue
        kind=status&0xf0
        if kind in (0xc0,0xd0):i+=1;continue
        if i+1>=len(chunk):raise ValueError('truncated midi event')
        a,b=chunk[i],chunk[i+1];i+=2
        if kind==0x90:events.append((tick,a,b>0))
        elif kind==0x80:events.append((tick,a,False))
    return {'name':name,'tempos':tempos,'events':events,'lastTick':last_tick}

def tick_seconds(tick,ppq,tempo_events):
    elapsed=0.0;last=0;tempo=500000
    for t,new in tempo_events:
        if t>tick:break
        elapsed+=(t-last)*tempo/1_000_000.0/ppq;last=t;tempo=new
    return elapsed+(tick-last)*tempo/1_000_000.0/ppq

def midi_string_events(path):
    data=Path(path).read_bytes()
    if data[:4]!=b'MThd':raise ValueError('missing MThd')
    hlen=struct.unpack('>I',data[4:8])[0]
    fmt,ntracks,division=struct.unpack('>HHH',data[8:14])
    if division&0x8000:raise ValueError('SMPTE MIDI unsupported')
    pos=8+hlen;tracks=[]
    for _ in range(ntracks):
        if data[pos:pos+4]!=b'MTrk':raise ValueError('missing MTrk')
        n=struct.unpack('>I',data[pos+4:pos+8])[0]
        tracks.append(parse_track(data[pos+8:pos+8+n]));pos+=8+n
    tempos=[(0,500000)]
    for t in tracks:tempos.extend(t['tempos'])
    tempo_map={}
    for tick,tempo in sorted(tempos):tempo_map[tick]=tempo
    tempo_events=sorted(tempo_map.items())
    out={}
    for tr in tracks:
        if tr['name'] not in CANON:continue
        active=defaultdict(list);notes=[]
        for tick,pitch,on in tr['events']:
            if on:active[pitch].append(tick)
            elif active[pitch]:
                start=active[pitch].pop(0)
                if tick>start:notes.append((tick_seconds(start,division,tempo_events),tick_seconds(tick,division,tempo_events),pitch))
        for pitch,starts in active.items():
            for start in starts:
                if tr['lastTick']>start:notes.append((tick_seconds(start,division,tempo_events),tick_seconds(tr['lastTick'],division,tempo_events),pitch))
        out[tr['name']]=sorted(notes)
    return out

def performance_key(path):
    stem=path.stem;parent=path.parent.name
    for prefix in (parent+'_','midi_','directinput_','micamp_','ego_','exo_'):
        if stem.lower().startswith(prefix.lower()) and len(stem)>len(prefix):return stem[len(prefix):]
    return stem

def visible_files(root):
    return sorted(p for p in Path(root).rglob('*') if p.is_file() and '__MACOSX' not in p.parts and p.name!='.DS_Store' and not p.name.startswith('._'))

def decode_audio(path):
    cmd=['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-i',str(path),'-vn','-ac','1','-ar',str(SAMPLE_RATE_HZ),'-f','f32le','-acodec','pcm_f32le','pipe:1']
    r=subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    x=np.frombuffer(r.stdout,dtype='<f4').copy()
    if x.size==0:raise ValueError('empty decoded audio')
    return x

def labels_for_frames(events,frames,lag_ms):
    labels=np.full((NUM_STRINGS,frames),-1,dtype=np.int16)
    times=np.arange(frames,dtype=np.float64)*HOP_LENGTH_SAMPLES/SAMPLE_RATE_HZ
    lag=lag_ms/1000.0
    for s,name in enumerate(STRING_ORDER):
        for start,end,pitch in events.get(name,[]):
            start+=lag;end+=lag
            if end<=0 or end<=start:continue
            i0=max(0,int(np.searchsorted(times,start,side='left')))
            i1=min(frames,int(np.searchsorted(times,end,side='left')))
            if i1<=i0:continue
            fret=int(pitch)-OPEN_MIDI[name]
            seg=labels[s,i0:i1]
            if fret<0 or fret>19:
                seg[:]=MASK;continue
            conflict=(seg!= -1)&(seg!=fret)
            seg[conflict]=MASK
            seg[seg==-1]=fret
    return labels

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def prepare_archive(args):
    corr=json.loads(Path(args.corrections).read_text())['correctionsMs']
    wanted={k:v for k,v in corr.items() if k.startswith(args.performer+'|'+args.category+'|')}
    root=Path(args.root);files=visible_files(root)
    midis={};audio=defaultdict(dict)
    for p in files:
        key=performance_key(p);s=p.suffix.lower()
        if s in ('.mid','.midi'):midis[key]=p
        elif s in ('.wav','.mp3'):audio[key][p.parent.name]=p
    outdir=Path(args.output_dir);outdir.mkdir(parents=True,exist_ok=True)
    manifest=Path(args.manifest);produced=[]
    for fullkey,lag in sorted(wanted.items()):
        performer,category,pkey,view=fullkey.split('|',3)
        if pkey not in midis or view not in audio.get(pkey,{}):raise RuntimeError('missing accepted source '+fullkey)
        wav=decode_audio(audio[pkey][view])
        feats=extract_cqt_features(rms_normalize(wav)).squeeze(0).astype(np.float32,copy=False)
        events=midi_string_events(midis[pkey])
        labels=labels_for_frames(events,feats.shape[-1],lag)
        ident=hashlib.sha256(fullkey.encode()).hexdigest()[:24]
        ff=outdir/(ident+'.features.npy');lf=outdir/(ident+'.labels.npy')
        np.save(ff,feats,allow_pickle=False);np.save(lf,labels,allow_pickle=False)
        rec={'key':fullkey,'performer':performer,'category':category,'performanceKey':pkey,'captureView':view,'lagMs':lag,'frames':int(feats.shape[-1]),'featureFile':ff.name,'labelFile':lf.name,'featureSha256':sha256_file(ff),'labelSha256':sha256_file(lf),'maskedStringFrames':int(np.sum(labels==MASK))}
        with manifest.open('a',encoding='utf-8') as fh:fh.write(json.dumps(rec,sort_keys=True)+'\n')
        produced.append(fullkey)
    if set(produced)!=set(wanted):raise RuntimeError('accepted correction set mismatch')
    print(json.dumps({'archive':args.archive,'prepared':len(produced),'performer':args.performer,'category':args.category},sort_keys=True))

def load_manifest(path,data_dir):
    rows=[]
    for line in Path(path).read_text().splitlines():
        if line.strip():
            r=json.loads(line);r['_features']=str(Path(data_dir)/r['featureFile']);r['_labels']=str(Path(data_dir)/r['labelFile']);rows.append(r)
    return rows

def get_window(feat,idx):
    out=np.zeros((feat.shape[0],FRAME_CONTEXT),dtype=np.float32)
    lo=max(0,idx-HALF_CONTEXT);hi=min(feat.shape[1],idx+HALF_CONTEXT+1)
    dst=HALF_CONTEXT-(idx-lo);out[:,dst:dst+(hi-lo)]=feat[:,lo:hi]
    return out

def masked_loss(logits,labels):
    b=labels.shape[0];x=logits.reshape(b,1,NUM_STRINGS,NUM_CLASSES)[:,0]
    target=labels.clone();target[target==-1]=NUM_CLASSES-1
    flat=F.cross_entropy(x.reshape(-1,NUM_CLASSES),target.reshape(-1),ignore_index=MASK,reduction='none').reshape(b,NUM_STRINGS)
    valid=(target!=MASK);count=valid.sum(1).clamp(min=1)
    return ((flat*valid).sum(1)*NUM_STRINGS/count).mean()

def state_sha256(model):
    h=hashlib.sha256()
    for name,value in sorted(model.state_dict().items()):
        t=value.detach().cpu().contiguous();h.update(name.encode());h.update(b'\0');h.update(str(t.dtype).encode());h.update(b'\0');h.update(','.join(map(str,t.shape)).encode());h.update(b'\0');h.update(t.numpy().tobytes())
    return h.hexdigest()

def infer(model,feat,batch=1024):
    pad=np.pad(feat,((0,0),(HALF_CONTEXT,HALF_CONTEXT)))
    windows=np.lib.stride_tricks.sliding_window_view(pad,FRAME_CONTEXT,axis=1).transpose(1,0,2)
    pred=np.empty((feat.shape[1],NUM_STRINGS),dtype=np.int16)
    model.eval()
    with torch.no_grad():
        for lo in range(0,len(windows),batch):
            w=np.ascontiguousarray(windows[lo:lo+batch])[:,None,None,:,:]
            logits=model(torch.from_numpy(w))['tablature']
            y=logits.reshape(-1,1,NUM_STRINGS,NUM_CLASSES)[:,0].argmax(-1).cpu().numpy().astype(np.int16)
            y[y==NUM_CLASSES-1]=-1;pred[lo:lo+len(y)]=y
    return pred

def runs(states,mask,string_idx):
    x=states[:,string_idx];m=mask[:,string_idx]
    valid=(~m)&(x>=0)
    if not np.any(valid):return []
    change=np.ones(len(x),dtype=bool);change[1:]=(x[1:]!=x[:-1])|(valid[1:]!=valid[:-1])
    starts=np.flatnonzero(change&valid)
    ev=[]
    hop=HOP_LENGTH_SAMPLES/SAMPLE_RATE_HZ
    for st in starts:
        en=st+1
        while en<len(x) and valid[en] and x[en]==x[st]:en+=1
        ev.append({'string':string_idx,'fret':int(x[st]),'start':st*hop,'end':en*hop})
    return ev

def match_group(pred,ref):
    n,m=len(pred),len(ref)
    dp=[[None]*(m+1) for _ in range(n+1)]
    for i in range(n+1):dp[i][0]=(0,0.0,())
    for j in range(m+1):dp[0][j]=(0,0.0,())
    for i in range(1,n+1):
        for j in range(1,m+1):
            opts=[dp[i-1][j],dp[i][j-1]]
            d=abs(pred[i-1]['start']-ref[j-1]['start'])
            if d<=ONSET_TOLERANCE:
                c,cost,pairs=dp[i-1][j-1];opts.append((c+1,cost+d,pairs+((i-1,j-1),)))
            dp[i][j]=min(opts,key=lambda z:(-z[0],z[1],z[2]))
    return dp[n][m][2]

def capture_metrics(pred,ref):
    mask=(ref==MASK);pred=pred.copy();pred[mask.T]=-1
    pe=[];re=[]
    # labels are 6 x T; runs expects T x 6
    rt=ref.T; mt=mask.T
    for s in range(NUM_STRINGS):
        pe+=runs(pred,mt,s)
        re+=runs(rt,mt,s)
    groups=defaultdict(lambda:[[],[]])
    for e in pe:groups[(e['string'],e['fret'])][0].append(e)
    for e in re:groups[(e['string'],e['fret'])][1].append(e)
    tp=0;overlap=0.0
    for key,(ps,rs) in groups.items():
        ps=sorted(ps,key=lambda e:e['start']);rs=sorted(rs,key=lambda e:e['start'])
        pairs=match_group(ps,rs);tp+=len(pairs)
        for i,j in pairs:overlap+=max(0.0,min(ps[i]['end'],rs[j]['end'])-max(ps[i]['start'],rs[j]['start']))
    precision=tp/len(pe) if pe else (1.0 if not re else 0.0)
    recall=tp/len(re) if re else (1.0 if not pe else 0.0)
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    refdur=sum(e['end']-e['start'] for e in re);complete=overlap/refdur if refdur>0 else 0.0
    accs=[]
    for s in range(NUM_STRINGS):
        r=ref[s];p=pred[:,s];valid=(r!=MASK);active=valid&((r>=0)|(p>=0))
        if np.any(active):accs.append(float(np.mean(p[active]==r[active])))
    frame=float(np.mean(accs)) if accs else 0.0
    return {'precision':precision,'recall':recall,'f1':f1,'completeness':complete,'frameAccuracy':frame,'abstentionRate':0.0}

def aggregate_metrics(rows,model,data_dir):
    caps=[]
    cache={}
    for r in rows:
        feat=np.load(r['_features'],mmap_mode='r');ref=np.load(r['_labels'],mmap_mode='r')
        pred=infer(model,feat)
        m=capture_metrics(pred,ref)
        m.update({'key':r['key'],'performance':r['performer']+'|'+r['category']+'|'+r['performanceKey'],'category':r['category']})
        caps.append(m)
    perfs=defaultdict(list)
    for c in caps:perfs[c['performance']].append(c)
    perf_metrics=[]
    for key,views in sorted(perfs.items()):
        category=views[0]['category'];pm={'performance':key,'category':category}
        for f in ('precision','recall','f1','completeness','frameAccuracy','abstentionRate'):pm[f]=float(np.mean([v[f] for v in views]))
        perf_metrics.append(pm)
    fold={}
    for f in ('precision','recall','f1','completeness','frameAccuracy','abstentionRate'):fold[f]=float(np.mean([p[f] for p in perf_metrics]))
    fold['contentF1']={}
    for cat in ('chords','scales','singlenotes','techniques'):
        vals=[p['f1'] for p in perf_metrics if p['category']==cat]
        if cat=='techniques': fold['contentF1']['PalmMute']=float(np.mean(vals)) if vals else 0.0
        else: fold['contentF1'][cat]=float(np.mean(vals)) if vals else 0.0
    fold['performanceCount']=len(perf_metrics);fold['captureCount']=len(caps)
    return fold

def checkpoint_selection_rows(rows):
    by_perf=defaultdict(list)
    for r in rows: by_perf[r['category']+'|'+r['performanceKey']].append(r)
    chosen=[]
    quotas={'chords':4,'scales':4,'singlenotes':1,'techniques':1}
    view_priority={'directinput':0,'micamp':1,'ego':2,'exo':3}
    for cat,quota in quotas.items():
        perfs=sorted(k for k in by_perf if k.startswith(cat+'|'))[:quota]
        for key in perfs:
            views=sorted(by_perf[key],key=lambda r:(view_priority.get(r['captureView'],99),r['key']))
            if not views: raise RuntimeError('empty checkpoint-selection performance '+key)
            chosen.append(views[0])
    if len(chosen)!=10: raise RuntimeError('checkpoint-selection subset must contain 10 capture paths')
    return chosen

def qualifies(m,t):
    e=t['acceptanceThresholds']['eachFold']
    return m['precision']>=e['onsetStringFretPrecisionMin'] and m['recall']>=e['onsetStringFretRecallMin'] and m['f1']>=e['onsetStringFretF1Min'] and m['completeness']>=e['noteEventCompletenessMin'] and m['frameAccuracy']>=e['frameStringFretAccuracyMin'] and m['abstentionRate']<=e['abstentionRateMax'] and all(m['contentF1'][c]>=e['eachPrimaryContentClassOnsetStringFretF1Min'] for c in ('chords','scales','singlenotes','PalmMute'))

def sample_batch(groups,rng):
    xs=[];ys=[]
    for _ in range(BATCH_SIZE):
        for attempt in range(100):
            group=groups[rng.randint(len(groups))];r=group[rng.randint(len(group))]
            feat=np.load(r['_features'],mmap_mode='r');lab=np.load(r['_labels'],mmap_mode='r')
            idx=int(rng.randint(feat.shape[1]))
            y=lab[:,idx]
            if np.any(y!=MASK):break
        else:raise RuntimeError('unable to sample unmasked frame')
        xs.append(get_window(feat,idx));ys.append(y.copy())
    x=torch.from_numpy(np.stack(xs)[:,None,None,:,:]);y=torch.from_numpy(np.stack(ys).astype(np.int64))
    return x,y

def train_fold(args):
    random.seed(SEED);np.random.seed(SEED);torch.manual_seed(SEED);torch.use_deterministic_algorithms(True);torch.set_num_threads(max(1,min(4,os.cpu_count() or 1)))
    sys.path.insert(0,args.source_root)
    from amt_tools.models.tabcnn import TabCNN
    from amt_tools.tools.instrument import GuitarProfile
    from amt_tools.tools.constants import KEY_TABLATURE
    rows=load_manifest(args.manifest,args.data_dir)
    if len(rows)!=256:raise RuntimeError('prepared capture count must be 256')
    counts={p:sum(r['performer']==p for r in rows) for p in ('P1','P2')}
    if counts!={'P1':136,'P2':120}:raise RuntimeError('prepared performer count mismatch '+repr(counts))
    train=[r for r in rows if r['performer']==args.train_performer];val=[r for r in rows if r['performer']==args.val_performer]
    grouped=defaultdict(list)
    for r in train:grouped[r['performer']+'|'+r['category']+'|'+r['performanceKey']].append(r)
    groups=[grouped[k] for k in sorted(grouped)]
    thresholds=json.loads(Path(args.thresholds).read_text())
    selection_rows=checkpoint_selection_rows(val)
    model=TabCNN(dim_in=192,profile=GuitarProfile(tuning=['E2','A2','D3','G3','B3','E4'],num_frets=19),device='cpu')
    opt=torch.optim.Adadelta(model.parameters(),lr=1.0);rng=np.random.RandomState(SEED)
    checkpoints=[];bestq=None;bestany=None;start=time.time()
    for it in range(1,MAX_ITERATIONS+1):
        model.train();x,y=sample_batch(groups,rng);opt.zero_grad(set_to_none=True);logits=model(x)[KEY_TABLATURE];loss=masked_loss(logits,y)
        if not torch.isfinite(loss):raise RuntimeError('nonfinite training loss')
        loss.backward();opt.step()
        if it%CHECKPOINT_EVERY==0:
            metrics=aggregate_metrics(selection_rows,model,args.data_dir);q=qualifies(metrics,thresholds)
            rec={'iteration':it,'trainingLoss':float(loss.detach()),'qualified':q,'metrics':metrics,'stateSha256':state_sha256(model)}
            checkpoints.append(rec)
            rank=(metrics['f1'],metrics['completeness'],-metrics['abstentionRate'],-it)
            if bestany is None or rank>bestany[0]:bestany=(rank,rec,{k:v.detach().cpu().clone() for k,v in model.state_dict().items()})
            if q and (bestq is None or rank>bestq[0]):bestq=(rank,rec,{k:v.detach().cpu().clone() for k,v in model.state_dict().items()})
            print('CHECKPOINT='+json.dumps(rec,sort_keys=True),flush=True)
    selected=bestq or bestany
    if selected is None:raise RuntimeError('no checkpoint evaluated')
    _,sel,state=selected
    model.load_state_dict(state)
    full_metrics=aggregate_metrics(val,model,args.data_dir)
    full_qualified=qualifies(full_metrics,thresholds)
    out_model=Path(args.model_out)
    torch.save({'candidateId':'astra_guitartechs_tabcnn_v1','fold':args.fold,'iteration':sel['iteration'],'stateDict':state,'stateSha256':sel['stateSha256'],'sourceRevision':'f50309ad06dc734ddae5e3a0eda756fca221e2e7'},out_model)
    receipt={'schema':'astra-guitar-techs-real-training-fold-v1','fold':args.fold,'trainPerformer':args.train_performer,'validationPerformer':args.val_performer,'seed':SEED,'iterations':MAX_ITERATIONS,'validationCheckpoints':len(checkpoints),'selectionSubsetQualified':bestq is not None,'selected':sel,'fullValidationMetrics':full_metrics,'fullValidationQualified':full_qualified,'checkpointSelectionCaptureKeys':[r['key'] for r in selection_rows],'checkpointSummaries':checkpoints,'preparedCaptureCounts':counts,'trainingPerformanceCount':len(groups),'validationCaptureCount':len(val),'modelFileSha256':sha256_file(out_model),'wallSeconds':time.time()-start,'guards':{'p3Opened':False,'publishedCheckpointLoaded':False,'paidComputeUsed':False,'customerDeliveryEligible':False}}
    Path(args.result_out).write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print('TRAINING_RESULT='+json.dumps({'fold':args.fold,'selectionSubsetQualified':receipt['selectionSubsetQualified'],'fullValidationQualified':receipt['fullValidationQualified'],'iteration':sel['iteration'],'selectionMetrics':sel['metrics'],'fullValidationMetrics':full_metrics,'modelFileSha256':receipt['modelFileSha256']},sort_keys=True))

def self_test():
    ref=np.array([[0,0,-1,-1],[ -1,-1,1,1],[-1,-1,-1,-1],[-1,-1,-1,-1],[-1,-1,-1,-1],[-1,-1,-1,-1]],dtype=np.int16)
    pred=ref.T.copy();m=capture_metrics(pred,ref)
    assert m['f1']==1 and m['frameAccuracy']==1 and m['completeness']==1
    x=torch.randn(2,1,126);y=torch.tensor([[0,-1,1,2,3,4],[0,-1,1,2,3,MASK]])
    assert torch.isfinite(masked_loss(x,y))
    print('SELF_TEST_PASS')

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
    q=sub.add_parser('prepare-archive')
    for name in ('root','archive','performer','category','corrections','output-dir','manifest'):q.add_argument('--'+name,required=True)
    t=sub.add_parser('train-fold')
    for name in ('source-root','manifest','data-dir','thresholds','fold','train-performer','val-performer','result-out','model-out'):t.add_argument('--'+name,required=True)
    sub.add_parser('self-test')
    a=p.parse_args()
    if a.cmd=='prepare-archive':prepare_archive(a)
    elif a.cmd=='train-fold':train_fold(a)
    else:self_test()

if __name__=='__main__':main()
