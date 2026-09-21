import { buildAstraAnalyzerResult, normalizeAstraAnalyzerRequest } from './analysisContractAdapter.mjs';

function require(condition, message) {
  if (!condition) throw new Error(message);
}

function stageFromRolePipeline(rolePipelineResult) {
  const evaluation = rolePipelineResult?.evidenceEvaluation;
  const roleStatus = rolePipelineResult?.roleEvidenceStatus;
  const exposure = rolePipelineResult?.exposure;

  if (roleStatus === 'abstained') {
    return {
      extraction: {
        status: 'abstained',
        blockers: ['ROLE_EVIDENCE_ABSTAINED'],
        rolePresence: 'uncertain',
      },
      events: {
        status: 'abstained',
        blockers: [...new Set([
          ...(evaluation?.failureReasons ?? []),
          ...(exposure?.blockers ?? []),
        ])].sort(),
      },
    };
  }

  const accepted = evaluation?.acceptedForCompleteTab === true
    && rolePipelineResult?.pipeline !== null;

  return {
    extraction: {
      status: 'complete',
      blockers: [],
      rolePresence: 'present',
    },
    events: accepted
      ? { status: 'complete', blockers: [] }
      : {
        status: 'partial',
        blockers: [...new Set([
          ...(evaluation?.failureReasons ?? []),
          ...(exposure?.blockers ?? []),
          'ROLE_EVIDENCE_PIPELINE_INCOMPLETE',
        ])].sort(),
      },
  };
}

export function buildRoleEvidenceAstraAnalysis({
  request: rawRequest,
  rolePipelineResult,
  lineage = {},
} = {}) {
  const request = normalizeAstraAnalyzerRequest(rawRequest);
  require(rolePipelineResult && typeof rolePipelineResult === 'object', 'rolePipelineResult is required.');
  require(
    rolePipelineResult.requestedRole === request.transcriptionType,
    'ROLE_PIPELINE_REQUESTED_ROLE_MISMATCH',
  );
  require(
    rolePipelineResult.customerDeliveryEligible === false,
    'ROLE_PIPELINE_MUST_REMAIN_DELIVERY_BLOCKED',
  );

  const derived = stageFromRolePipeline(rolePipelineResult);
  const stages = {
    input: { status: 'complete', blockers: [] },
    extraction: derived.extraction,
    events: derived.events,
    structure: { status: 'complete', blockers: [] },
  };

  const result = buildAstraAnalyzerResult({
    request,
    stages,
    pipelineResult: rolePipelineResult.pipeline,
    lineage: {
      separator: lineage.separator ?? 'astra-role-evidence-development-v1',
      eventInference: lineage.eventInference ?? 'astra-role-evidence-deterministic-pipeline-v1',
      structure: lineage.structure ?? 'astra-frozen-structure-map-v1',
      tablature: lineage.tablature ?? 'astra-backend-deterministic-pipeline-v1',
    },
    // Development role evidence can never self-authorize customer delivery.
    deliveryPolicyVersion: null,
  });

  return {
    ...result,
    astra: {
      ...result.astra,
      roleEvidence: {
        integrationContract: rolePipelineResult.integrationContract?.name ?? null,
        roleEvidenceStatus: rolePipelineResult.roleEvidenceStatus,
        evidenceStateCounts: rolePipelineResult.adaptedEvidence?.metrics?.evidenceStateCounts ?? null,
        promotedEventCount: rolePipelineResult.adaptedEvidence?.metrics?.promotedEventCount ?? 0,
        customerDeliveryEligible: false,
      },
    },
  };
}
