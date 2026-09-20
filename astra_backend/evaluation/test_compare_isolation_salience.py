import hashlib,json,tempfile,unittest,wave
from pathlib import Path
import numpy as np
from compare_isolation_salience import compare

class IsolationSalienceTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);r=Path(self.t.name);self.src=r/'s.wav';self.iso=r/'i.wav';sr=22050;n=sr*2;t=np.arange(n)/sr;f=440*2**((60-69)/12)
  rng=np.random.default_rng(1);s=.02*rng.normal(size=n);i=.005*rng.normal(size=n)
  mask=(t>=.5)&(t<.65);s[mask]+=.02*np.sin(2*np.pi*f*t[mask]);i[mask]+=.15*np.sin(2*np.pi*f*t[mask])
  for p,x in [(self.src,s),(self.iso,i)]:
   with wave.open(str(p),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(x,-.9,.9)*32767).astype('<i2').tobytes())
  sh=hashlib.sha256(self.src.read_bytes()).hexdigest();self.sh=sh;self.ih=hashlib.sha256(self.iso.read_bytes()).hexdigest();self.lab=r/'l.json';self.al=r/'a.json'
  self.lab.write_text(json.dumps({'audioSha256':sh,'reviewStatus':'complete','unresolvedItems':[],'coverageReviewed':True,'events':[{'id':'x','kind':'attack','beat':1,'midi':60}]}))
  self.al.write_text(json.dumps({'audioSha256':sh,'reviewStatus':'complete','unresolvedItems':[],'independentOfPredictions':True,'segments':[{'beatStart':0,'beatEnd':4,'timeStart':0,'timeEnd':2}]}))
 def test_isolation_gain_is_positive(self):
  r=compare(self.src,self.iso,self.lab,self.al,source_sha256=self.sh,isolated_sha256=self.ih,offset=0,scale=1);self.assertGreater(r['overallMedianGainDb'],0.5);self.assertEqual(r['overallPositiveGainCount'],1);self.assertFalse(r['predictionsRead'])
 def test_audio_hash_mismatch_fails(self):
  with self.assertRaisesRegex(ValueError,'SHA256'):compare(self.src,self.iso,self.lab,self.al,source_sha256='0'*64,isolated_sha256=self.ih,offset=0,scale=1)
 def test_draft_labels_fail(self):
  d=json.loads(self.lab.read_text());d['reviewStatus']='draft';self.lab.write_text(json.dumps(d))
  with self.assertRaisesRegex(ValueError,'Labels'):compare(self.src,self.iso,self.lab,self.al,source_sha256=self.sh,isolated_sha256=self.ih,offset=0,scale=1)
if __name__=='__main__':unittest.main()
