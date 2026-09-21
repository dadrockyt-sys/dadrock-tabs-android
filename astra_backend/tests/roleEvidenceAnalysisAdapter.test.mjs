import test from 'node:test';
import assert from 'node:assert/strict';

import { buildRoleEvidenceAstraAnalysis } from '../roleEvidenceAnalysisAdapter.mjs';
import { runRoleEvidenceDeterministicPipeline } from '../roleEvidencePipelineAdapter.mjs';
import { buildStructureMap } from '../structureMap.mjs';

const TUNING = [40,45,50,55,59,64];

function map() {
  return buildStructureMap({
    durationSeconds: 4,
    pickupDurationSeconds: 0,
    tempoSegments: [{ start:0,end:null,bpm:120,confidence:1 }],
    meterSegments: [{ start:0,end:null,numerator:4,denominator:4,confidence:1 }],
    feelSegments: [{ start:0,end:null,feel:'straight',confidence:1 }],
    confidence: { overall:1,tempo:1,meter:1,downbeats:1,measures:1,feel:1 },
    provenance: { source:'role-analysis-test', referenceBlind:true },
  });
}

function request(role='lead', id='role-analysis') {
  return {
    contractName:'jimmy-paige-astra-analyzer-request',
    contractVersion:1,
    requestId:id,
    audioUrl:'https://example.invalid/role-analysis.wav',
    pathname:'fixtures/role-analysis.wav',
    song:'Synthetic Role Evidence',
    artist:'DadRock Tests',
    transcriptionType:role,
    conditioning:{
      structurePrior:{
        tempoBpm:120,
        timeSignature:{numerator:4,denominator:4},
        pickupBeats:0,
        feel:'straight',
      },
      instrumentConfig:{
        role,
        tuningMidi:[...TUNING],
        capoFret:0,
      },
    },
  };
}

function p(id,midi,start,state) {
  return {
    id,midi,start,duration:.25,durationConfidence:.9,
    confidence:.9,onsetConfidence:.9,
    provenance:{source:state},
  };
}

function completeRolePipeline() {
  return runRoleEvidenceDeterministicPipeline({
    requestedRole:'lead',
    roleEvidenceStatus:'complete',
    structureMap:map(),
    streams:{
      promotedCore:[p('core',64,0,'core')],
      promotedTechnique:[p('tech',67,.5,'technique')],
      recoveredRecurringOnset:[p('recover',69,1,'recovery')],
      ambiguous:[],unassigned:[],rejected:[],
    },
    capabilities:{
      polyphonyResolved:true,
      durationResolution:'complete',
      instrumentIsolation:'stereo-role-evidence',
      confidenceCalibration:'heuristic-not-calibrated-probability',
    },
    provenance:{source:'synthetic-role-evidence',modelInvoked:false},
    instrumentConfig:{role:'lead',tuningMidi:[...TUNING],capoFret:0},
  });
}

test('resolved role evidence reaches frontend-shaped result but remains delivery blocked without policy', () => {
  const rolePipelineResult=completeRolePipeline();
  const result=buildRoleEvidenceAstraAnalysis({
    request:request('lead'),
    rolePipelineResult,
  });
  assert.equal(result.generatedTab.includes('RIFF 1'),true);
  assert.equal(result.events.length,3);
  assert.deepEqual(result.renderEvents,[]);
  assert.equal(result.astra.overallStatus,'partial');
  assert.equal(result.astra.delivery.deliveryReady,false);
  assert.ok(result.astra.delivery.blockers.includes('delivery:DELIVERY_POLICY_MISSING'));
  assert.equal(result.astra.roleEvidence.customerDeliveryEligible,false);
  assert.deepEqual(result.astra.roleEvidence.evidenceStateCounts,{
    'promoted-core':1,
    'promoted-technique':1,
    'recovered-recurring-onset':1,
    ambiguous:0,
    unassigned:0,
    rejected:0,
  });
});

test('ambiguous role evidence yields no deterministic/frontend events', () => {
  const rolePipelineResult=runRoleEvidenceDeterministicPipeline({
    requestedRole:'lead',
    roleEvidenceStatus:'complete',
    structureMap:map(),
    streams:{
      promotedCore:[p('core',64,0,'core')],
      promotedTechnique:[],
      recoveredRecurringOnset:[],
      ambiguous:[{
        id:'amb',start:.5,onsetConfidence:.8,
        candidates:[{midi:67,confidence:.7},{midi:71,confidence:.68}],
      }],
      unassigned:[],rejected:[],
    },
    capabilities:{
      polyphonyResolved:true,
      durationResolution:'complete',
      instrumentIsolation:'stereo-role-evidence',
    },
    provenance:{source:'synthetic-role-evidence',modelInvoked:false},
    instrumentConfig:{role:'lead',tuningMidi:[...TUNING],capoFret:0},
  });
  const result=buildRoleEvidenceAstraAnalysis({request:request('lead','amb'),rolePipelineResult});
  assert.equal(result.astra.overallStatus,'partial');
  assert.equal(result.generatedTab,'');
  assert.deepEqual(result.events,[]);
  assert.deepEqual(result.renderEvents,[]);
  assert.equal(result.astra.delivery.deliveryReady,false);
});

test('abstained role evidence yields abstained frontend state and no invented tab', () => {
  const rolePipelineResult=runRoleEvidenceDeterministicPipeline({
    requestedRole:'lead',
    roleEvidenceStatus:'abstained',
    structureMap:map(),
    streams:{
      promotedCore:[],promotedTechnique:[],recoveredRecurringOnset:[],
      ambiguous:[{
        id:'amb',start:.5,onsetConfidence:.6,
        candidates:[{midi:64,confidence:.6}],
      }],
      unassigned:[],rejected:[],
    },
    capabilities:{
      polyphonyResolved:false,
      durationResolution:'none',
      instrumentIsolation:'unresolved',
    },
    provenance:{source:'synthetic-role-evidence',modelInvoked:false},
    instrumentConfig:{role:'lead',tuningMidi:[...TUNING],capoFret:0},
  });
  const result=buildRoleEvidenceAstraAnalysis({request:request('lead','abstain'),rolePipelineResult});
  assert.equal(result.astra.overallStatus,'abstained');
  assert.equal(result.generatedTab,'');
  assert.deepEqual(result.events,[]);
  assert.equal(result.astra.delivery.deliveryReady,false);
  assert.equal(result.astra.roleEvidence.roleEvidenceStatus,'abstained');
});

test('request and role pipeline roles must agree', () => {
  const rolePipelineResult=completeRolePipeline();
  assert.throws(
    () => buildRoleEvidenceAstraAnalysis({
      request:request('rhythm','mismatch'),
      rolePipelineResult,
    }),
    /ROLE_PIPELINE_REQUESTED_ROLE_MISMATCH/,
  );
});

test('analysis bridge is deterministic', () => {
  const rolePipelineResult=completeRolePipeline();
  const args={request:request('lead','deterministic'),rolePipelineResult};
  assert.deepEqual(buildRoleEvidenceAstraAnalysis(args),buildRoleEvidenceAstraAnalysis(args));
});
