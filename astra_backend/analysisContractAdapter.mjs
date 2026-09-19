const REQUEST_CONTRACT = 'jimmy-paige-astra-analyzer-request';
const RESULT_CONTRACT = 'jimmy-paige-astra-analyzer-result';
const CONTRACT_VERSION = 1;
const ROLES = new Set(['lead', 'rhythm', 'bass']);
const FEELS = new Set(['auto', 'straight', 'triplet']);
const STAGE_STATUSES = new Set(['complete', 'partial', 'abstained', 'failed', 'not-run']);
const STAGE_NAMES = ['input', 'extraction', 'events', 'structure'];

function object(value, field) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error(`${field} must be an object.`);
  }
  return value;
}

function text(value, field, maximumLength) {
  if (typeof value !== 'string' || !value.trim()) throw new Error(`${field} is required.`);
  const normalized = value.trim();
  if (normalized.length > maximumLength) throw new Error(`${field} is too long.`);
  return normalized;
}

function blockers(values = []) {
  if (!Array.isArray(values)) throw new Error('stage blockers must be an array.');
  return [...new Set(values.map((value) => String(value).trim()).filter(Boolean))].sort();
}

function normalizeTimeSignature(value) {
  if (value === 'auto') return 'auto';
  const input = object(value, 'conditioning.structurePrior.timeSignature');
  const allowed = new Set([1, 2, 4, 8, 16, 32]);
  if (!Number.isInteger(input.numerator) || input.numerator < 1 || input.numerator > 32) {
    throw new Error('timeSignature.numerator must be an integer from 1 to 32.');
  }
  if (!Number.isInteger(input.denominator) || !allowed.has(input.denominator)) {
    throw new Error('timeSignature.denominator is invalid.');
  }
  return { numerator: input.numerator, denominator: input.denominator };
}

function autoOrFinite(value, field, minimum, maximum) {
  if (value === 'auto') return 'auto';
  if (!Number.isFinite(value) || value < minimum || value > maximum) {
    throw new Error(`${field} must be auto or between ${minimum} and ${maximum}.`);
  }
  return value;
}

function normalizeTuning(value, role) {
  if (value === 'auto') return 'auto';
  if (!Array.isArray(value)) throw new Error('instrumentConfig.tuningMidi must be auto or an array.');
  const maximum = role === 'bass' ? 6 : 8;
  if (value.length < 4 || value.length > maximum) {
    throw new Error(`instrumentConfig.tuningMidi must contain 4-${maximum} strings for ${role}.`);
  }
  value.forEach((midi, index) => {
    if (!Number.isInteger(midi) || midi < 0 || midi > 127) {
      throw new Error('Every tuning MIDI value must be an integer from 0 to 127.');
    }
    if (index > 0 && midi <= value[index - 1]) {
      throw new Error('instrumentConfig.tuningMidi must increase from lowest to highest string.');
    }
  });
  return [...value];
}

export function normalizeAstraAnalyzerRequest(raw) {
  const input = object(raw, 'request');
  if (input.contractName !== REQUEST_CONTRACT || input.contractVersion !== CONTRACT_VERSION) {
    throw new Error('Unsupported Astra analyzer request contract.');
  }
  const role = input.transcriptionType;
  if (!ROLES.has(role)) throw new Error('transcriptionType must be lead, rhythm, or bass.');
  const conditioning = object(input.conditioning, 'conditioning');
  const structure = object(conditioning.structurePrior, 'conditioning.structurePrior');
  const instrument = object(conditioning.instrumentConfig, 'conditioning.instrumentConfig');
  if (instrument.role !== role) throw new Error('instrumentConfig.role must match transcriptionType.');
  if (!FEELS.has(structure.feel)) throw new Error('structurePrior.feel is invalid.');
  const capoFret = instrument.capoFret;
  if (capoFret !== 'auto' && (!Number.isInteger(capoFret) || capoFret < 0 || capoFret > 24)) {
    throw new Error('instrumentConfig.capoFret must be auto or an integer from 0 to 24.');
  }

  return {
    contractName: REQUEST_CONTRACT,
    contractVersion: CONTRACT_VERSION,
    requestId: text(input.requestId, 'requestId', 200),
    audioUrl: text(input.audioUrl, 'audioUrl', 2000),
    pathname: text(input.pathname, 'pathname', 1000),
    song: text(input.song, 'song', 120),
    artist: text(input.artist, 'artist', 120),
    transcriptionType: role,
    conditioning: {
      structurePrior: {
        tempoBpm: autoOrFinite(structure.tempoBpm, 'structurePrior.tempoBpm', 20, 400),
        timeSignature: normalizeTimeSignature(structure.timeSignature),
        pickupBeats: autoOrFinite(structure.pickupBeats, 'structurePrior.pickupBeats', 0, 32),
        feel: structure.feel,
      },
      instrumentConfig: {
        role,
        tuningMidi: normalizeTuning(instrument.tuningMidi, role),
        capoFret,
      },
    },
  };
}

function normalizeStage(raw, name) {
  const input = object(raw, `stages.${name}`);
  if (!STAGE_STATUSES.has(input.status)) throw new Error(`stages.${name}.status is invalid.`);
  const normalizedBlockers = blockers(input.blockers);
  if (input.status === 'complete' && normalizedBlockers.length) {
    throw new Error(`A complete ${name} stage cannot contain blockers.`);
  }
  return { ...input, status: input.status, blockers: normalizedBlockers };
}

function deriveTablatureStage(pipelineResult, role) {
  if (!pipelineResult) return { status: 'not-run', blockers: ['TABLATURE_PIPELINE_NOT_RUN'] };
  const shell = pipelineResult.productShell;
  if (!shell?.payloadContract) return { status: 'failed', blockers: ['TABLATURE_PRODUCT_SHELL_MISSING'] };
  const foundRole = shell.transcriptionType;
  if (foundRole !== role) return { status: 'failed', blockers: ['TABLATURE_ROLE_MISMATCH'] };
  if (!shell.payloadContract.deliveryReady) {
    return { status: 'partial', blockers: ['TABLATURE_UPSTREAM_OR_INTEGRITY_BLOCKED'] };
  }
  if (!shell.payloadContract.structuredRenderEligible || !shell.renderEvents?.length) {
    return {
      status: 'partial',
      blockers: [shell.payloadContract.legacyProjectionReason || 'TABLATURE_RENDER_EVENTS_UNAVAILABLE'],
    };
  }
  if (!shell.generatedTab) return { status: 'partial', blockers: ['TABLATURE_TEXT_EMPTY'] };
  return { status: 'complete', blockers: [] };
}

function eventPayload(event, requestId, index) {
  const sourceIndex = Number.isInteger(event?.sourceEventIndex) ? event.sourceEventIndex : index;
  const onset = Number(event?.sourceStart);
  const duration = Number(event?.sourceDurationSeconds);
  const end = Number(event?.sourceEnd);
  const resolvedOffset = Number.isFinite(end)
    ? end
    : (Number.isFinite(duration) && Number.isFinite(onset) ? onset + duration : null);
  return {
    eventId: `${requestId}:event:${sourceIndex}`,
    midi: event.midi,
    onsetSeconds: onset,
    offsetSeconds: resolvedOffset,
    durationStatus: resolvedOffset === null ? 'unresolved' : 'resolved',
    sourceIdentity: `${requestId}:source:${sourceIndex}`,
    sourceEventIndex: sourceIndex,
    measureNumber: event.measureNumber ?? null,
    beatNumber: event.beatNumber ?? null,
    fretboard: event.fretboard ?? null,
  };
}

function overallStatus(stages, rolePresence, policyPresent, productReady) {
  if (Object.values(stages).some((stage) => stage.status === 'failed')) return 'failed';
  if (rolePresence === 'absent' || rolePresence === 'uncertain'
    || Object.values(stages).some((stage) => stage.status === 'abstained')) return 'abstained';
  if (Object.values(stages).every((stage) => stage.status === 'complete')
    && policyPresent && productReady) return 'complete';
  return 'partial';
}

export function buildAstraAnalyzerResult({
  request: rawRequest,
  stages: rawStages,
  pipelineResult = null,
  lineage = {},
  deliveryPolicyVersion = null,
} = {}) {
  const request = normalizeAstraAnalyzerRequest(rawRequest);
  const providedStages = object(rawStages, 'stages');
  const stages = Object.fromEntries(STAGE_NAMES.map((name) => [
    name,
    normalizeStage(providedStages[name], name),
  ]));
  stages.tablature = deriveTablatureStage(pipelineResult, request.transcriptionType);

  const rolePresence = stages.extraction.rolePresence ?? 'uncertain';
  if (!new Set(['present', 'absent', 'uncertain']).has(rolePresence)) {
    throw new Error('stages.extraction.rolePresence is invalid.');
  }
  if (rolePresence !== 'present' && stages.extraction.status === 'complete') {
    throw new Error('A complete extraction stage requires rolePresence present.');
  }

  const shell = pipelineResult?.productShell ?? null;
  const productReady = Boolean(
    shell?.payloadContract?.deliveryReady
      && shell?.payloadContract?.structuredRenderEligible
      && shell?.generatedTab
      && shell?.renderEvents?.length,
  );
  const policyVersion = typeof deliveryPolicyVersion === 'string' && deliveryPolicyVersion.trim()
    ? deliveryPolicyVersion.trim()
    : null;
  const status = overallStatus(stages, rolePresence, Boolean(policyVersion), productReady);
  const deliveryReady = status === 'complete';
  const deliveryBlockers = blockers([
    ...Object.entries(stages).flatMap(([name, stage]) => stage.blockers.map((item) => `${name}:${item}`)),
    ...(rolePresence === 'present' ? [] : [`extraction:ROLE_${rolePresence.toUpperCase()}`]),
    ...(policyVersion ? [] : ['delivery:DELIVERY_POLICY_MISSING']),
    ...(productReady ? [] : ['delivery:PRODUCT_PAYLOAD_NOT_READY']),
  ]);

  const events = (pipelineResult?.events ?? []).map((event, index) => (
    eventPayload(event, request.requestId, index)
  ));

  return {
    generatedTab: shell?.generatedTab ?? '',
    transcriptionType: request.transcriptionType,
    tuning: shell?.tuning ?? null,
    tempo: shell?.tempo ?? null,
    timeSignature: shell?.timeSignature ?? null,
    keySignature: shell?.keySignature ?? null,
    techniques: Array.isArray(shell?.techniques) ? [...shell.techniques] : [],
    analysisEngine: 'jimmy-paige-astra-offline-adapter-v1',
    events,
    renderEvents: deliveryReady ? [...shell.renderEvents] : [],
    astra: {
      contractName: RESULT_CONTRACT,
      contractVersion: CONTRACT_VERSION,
      requestId: request.requestId,
      overallStatus: status,
      stages,
      delivery: {
        deliveryReady,
        blockers: deliveryReady ? [] : deliveryBlockers,
        policyVersion,
      },
      lineage: {
        separator: lineage.separator ?? null,
        eventInference: lineage.eventInference ?? null,
        structure: lineage.structure ?? null,
        tablature: lineage.tablature ?? 'astra-backend-deterministic-pipeline-v1',
      },
    },
  };
}
