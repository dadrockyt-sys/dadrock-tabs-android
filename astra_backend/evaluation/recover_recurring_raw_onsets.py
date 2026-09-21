"""Reference-blind completion of internal recurring-pattern gaps from raw onset evidence."""
from __future__ import annotations

import math
import numpy as np

from extract_raw_bend_starts import MIDI_OFFSET, model_frame_times, local_onset_peaks, require, validate_raw

ONSET_THRESHOLD = 0.5
ONSET_SEARCH_TOLERANCE_SECONDS = 0.05
MIN_DISTINCT_MEASURE_SUPPORT = 3
FLOAT_EPSILON = 1e-9


def finite(v):
    return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)


def validate_alignment(alignment):
    require(isinstance(alignment,dict), 'alignment must be an object')
    require(alignment.get('reviewStatus')=='complete', 'alignment must be complete')
    require(alignment.get('independentOfPredictions') is True, 'alignment must be prediction-independent')
    segs=alignment.get('segments')
    require(isinstance(segs,list) and len(segs)>=MIN_DISTINCT_MEASURE_SUPPORT, 'alignment segments missing')
    return segs


def source_time_for_position(measure_index, relative_beat, segments):
    require(1 <= measure_index <= len(segments), 'measure index outside alignment')
    s=segments[measure_index-1]
    beat=s['beatStart']+relative_beat
    require(s['beatStart']-FLOAT_EPSILON <= beat < s['beatEnd']-FLOAT_EPSILON, 'relative beat outside measure')
    alpha=(beat-s['beatStart'])/(s['beatEnd']-s['beatStart'])
    return s['timeStart']+alpha*(s['timeEnd']-s['timeStart'])


def nearest_existing(events, midi, source_time, tolerance=ONSET_SEARCH_TOLERANCE_SECONDS):
    rows=[e for e in events if e.get('midi')==midi and finite(e.get('start')) and abs(e['start']-source_time)<=tolerance+FLOAT_EPSILON]
    return min(rows,key=lambda e:(abs(e['start']-source_time),e.get('id',''))) if rows else None


def raw_peak_for(raw, midi, isolated_time, tolerance=ONSET_SEARCH_TOLERANCE_SECONDS):
    validate_raw(raw)
    b=midi-MIDI_OFFSET
    if not 0 <= b < raw['onset'].shape[1]:
        return None
    times=model_frame_times(raw['onset'].shape[0])
    column=raw['onset'][:,b]
    peaks=local_onset_peaks(column)
    candidates=[int(f) for f in peaks if abs(float(times[f])-isolated_time)<=tolerance+FLOAT_EPSILON]
    if not candidates:
        return None
    frame=max(candidates,key=lambda f:(float(column[f]),-abs(float(times[f])-isolated_time),-f))
    activation=float(column[frame])
    if activation < ONSET_THRESHOLD:
        return None
    return {'frame':frame,'isolatedTime':float(times[frame]),'onsetActivation':activation}


def recover(partition, raw, alignment, existing_events, *, affine_offset, affine_scale):
    require(isinstance(partition,dict) and partition.get('status')=='complete', 'recurring partition must be complete')
    require(partition.get('diagnostics',{}).get('referenceLabelsRead') is False, 'partition must be reference-blind')
    require(finite(affine_offset) and finite(affine_scale) and affine_scale>0, 'invalid affine transform')
    segments=validate_alignment(alignment)
    core=partition.get('recurringCoreEvents')
    require(isinstance(core,list), 'recurring core missing')
    existing=list(existing_events)
    support={}
    for row in core:
        rep=row.get('repeatEvidence',{})
        key=(row.get('midi'),rep.get('relativeBeat'))
        require(isinstance(key[0],int) and finite(key[1]), 'invalid recurring key')
        support.setdefault(key,set()).add(int(rep['measureIndex']))
    proposals=[]
    for (midi,relative),measures in sorted(support.items()):
        if len(measures)<MIN_DISTINCT_MEASURE_SUPPORT:
            continue
        lo,hi=min(measures),max(measures)
        for measure in range(lo+1,hi):
            if measure in measures:
                continue
            source_slot=source_time_for_position(measure,relative,segments)
            decoded=nearest_existing(existing,midi,source_slot)
            if decoded is not None:
                proposals.append({
                    **decoded,
                    'id':f'recur-existing-{decoded.get("id",measure)}',
                    'recoveryEvidence':{
                        'kind':'existing-decoded-recurring-gap',
                        'measureIndex':measure,'relativeBeat':relative,
                        'distinctMeasureSupport':len(measures),
                        'sourceGridTime':source_slot,
                    }
                })
                continue
            isolated_slot=affine_offset+affine_scale*source_slot
            peak=raw_peak_for(raw,midi,isolated_slot)
            if peak is None:
                continue
            source_onset=(peak['isolatedTime']-affine_offset)/affine_scale
            require(abs(source_onset-source_slot)<=ONSET_SEARCH_TOLERANCE_SECONDS+FLOAT_EPSILON,
                    'projected onset escaped grid tolerance')
            proposals.append({
                'id':f'recur-raw-m{measure}-b{relative:g}-midi{midi}',
                'midi':midi,'start':source_onset,
                'onsetConfidence':peak['onsetActivation'],
                'recoveryEvidence':{
                    'kind':'raw-onset-recurring-gap',
                    'measureIndex':measure,'relativeBeat':relative,
                    'distinctMeasureSupport':len(measures),
                    'sourceGridTime':source_slot,
                    'rawFrame':peak['frame'],'isolatedOnsetTime':peak['isolatedTime'],
                    'onsetThreshold':ONSET_THRESHOLD,
                }
            })
    kept=[]
    inventory=list(core)
    for row in sorted(proposals,key=lambda e:(e['start'],e['midi'],e['id'])):
        if nearest_existing(inventory,row['midi'],row['start']) is not None:
            continue
        kept.append(row)
        inventory.append(row)
    return {
        'kind':'recurring-raw-onset-gap-recovery',
        'version':1,
        'recoveredEvents':kept,
        'diagnostics':{
            'referenceLabelsRead':False,
            'onsetThreshold':ONSET_THRESHOLD,
            'onsetSearchToleranceSeconds':ONSET_SEARCH_TOLERANCE_SECONDS,
            'minDistinctMeasureSupport':MIN_DISTINCT_MEASURE_SUPPORT,
            'internalGapsOnly':True,
            'eventMidiComesOnlyFromPreviouslyObservedRecurringKey':True,
            'leadingAndTrailingExtrapolationAllowed':False,
            'recoveredEventCount':len(kept),
        },
        'customerDeliveryEligible':False,
    }
