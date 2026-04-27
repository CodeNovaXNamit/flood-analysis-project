'use server';

import { z } from 'genkit';
import { googleAI } from '@genkit-ai/google-genai';

import { ai } from '@/ai/genkit';

const RiskPrioritySchema = z.enum(['CRITICAL', 'HIGH', 'MEDIUM']);
const EscalationLevelSchema = z.enum(['SEVERE', 'ELEVATED', 'GUARDED', 'STABLE']);

const TopWardSchema = z.object({
  wardId: z.string(),
  wardName: z.string(),
  risk: z.number(),
  populationAffected: z.number(),
  trend: z.enum(['increasing', 'stable', 'decreasing']),
});

const LatestRunSummarySchema = z.object({
  status: z.string(),
  latestPredictionDate: z.string().nullable(),
  outputRows: z.number().nullable(),
  maxRisk: z.number().nullable(),
  meanRisk: z.number().nullable(),
  highRiskPoints: z.number().nullable(),
  mediumRiskPoints: z.number().nullable(),
  lowRiskPoints: z.number().nullable(),
});

const MitigationInputSchema = z.object({
  cityReadiness: z.number(),
  hotspotsCount: z.number(),
  rainfallMm: z.number(),
  weatherCondition: z.string(),
  avgRiskPercent: z.number(),
  totalPopulationAtRisk: z.number(),
  topWards: z.array(TopWardSchema).max(5),
  latestRun: LatestRunSummarySchema.nullable(),
});

const MitigationOutputSchema = z.object({
  strategicSummary: z.string(),
  escalationLevel: EscalationLevelSchema,
  actions: z.array(
    z.object({
      priority: RiskPrioritySchema,
      task: z.string(),
      rationale: z.string(),
    })
  ).min(3).max(5),
  wardFocus: z.array(
    z.object({
      wardName: z.string(),
      reason: z.string(),
    })
  ).min(2).max(4),
  riskProjection: z.string(),
  publicAdvisory: z.string(),
  groundingNotes: z.string(),
  source: z.enum(['Gemini', 'Fallback']),
  modelUsed: z.string(),
  generatedAt: z.string(),
});

export type MitigationInput = z.infer<typeof MitigationInputSchema>;
export type MitigationOutput = z.infer<typeof MitigationOutputSchema>;

function hasGoogleAiKey(): boolean {
  return Boolean(
    process.env.GEMINI_API_KEY ||
    process.env.GOOGLE_API_KEY ||
    process.env.GOOGLE_GENAI_API_KEY
  );
}

function buildFallbackAdvice(input: MitigationInput): MitigationOutput {
  const firstWard = input.topWards[0]?.wardName ?? 'highest-risk ward cluster';
  const secondWard = input.topWards[1]?.wardName ?? 'secondary hotspot corridor';
  const severe = input.rainfallMm >= 25 || input.hotspotsCount >= 12 || input.cityReadiness <= 40;
  const elevated = input.rainfallMm >= 12 || input.hotspotsCount >= 6 || input.cityReadiness <= 60;

  const escalationLevel: MitigationOutput['escalationLevel'] = severe
    ? 'SEVERE'
    : elevated
      ? 'ELEVATED'
      : input.cityReadiness >= 75
        ? 'STABLE'
        : 'GUARDED';

  const strategicSummary = severe
    ? 'Flood pressure is elevated across multiple wards and immediate field coordination is advised.'
    : elevated
      ? 'Localized flood risk is building and pre-positioning crews will reduce response time.'
      : 'System indicators remain manageable, but continuous monitoring and ward-level readiness checks should continue.';

  const actions: MitigationOutput['actions'] = severe
    ? [
        {
          priority: 'CRITICAL',
          task: `Pre-position pumping and response crews near ${firstWard}`,
          rationale: 'Top-risk wards should receive equipment first because they are most likely to experience drainage stress and rapid accumulation.',
        },
        {
          priority: 'HIGH',
          task: 'Inspect critical outfalls and drain choke points within the next operational cycle',
          rationale: 'High rainfall combined with hotspot density suggests that blocked drainage can escalate localized flooding quickly.',
        },
        {
          priority: 'HIGH',
          task: 'Prepare ward control rooms for citizen escalation and route management',
          rationale: 'Operational readiness improves when response communication, public updates, and field routing are coordinated before inundation peaks.',
        },
      ]
    : [
        {
          priority: 'HIGH',
          task: `Run targeted maintenance sweeps in ${firstWard}`,
          rationale: 'The most exposed ward should be stabilized early to prevent cascading drainage failures.',
        },
        {
          priority: 'MEDIUM',
          task: `Monitor flood trend progression in ${secondWard}`,
          rationale: 'The second-highest ward often acts as an early signal for broader geographic spread.',
        },
        {
          priority: 'MEDIUM',
          task: 'Keep field teams on standby and refresh telemetry every cycle',
          rationale: 'Moderate risk conditions benefit from frequent reassessment rather than delayed manual review.',
        },
      ];

  return {
    strategicSummary,
    escalationLevel,
    actions,
    wardFocus: [
      {
        wardName: firstWard,
        reason: 'Highest modeled exposure based on current ward risk and population impact signals.',
      },
      {
        wardName: secondWard,
        reason: 'Secondary focus zone for preventive action and overflow monitoring.',
      },
    ],
    riskProjection: severe
      ? 'If rainfall intensity persists, additional hotspot growth and transport disruption are likely in the next 2 to 6 hours.'
      : 'If current conditions hold, localized flooding can remain contained with targeted municipal intervention.',
    publicAdvisory: severe
      ? 'Advise field teams and local administrators to prepare for rapid response in low-lying and high-density wards.'
      : 'Maintain alerts for local drainage teams and continue cautionary communication in sensitive wards.',
    groundingNotes: 'Fallback mode used because no Google AI API key was available or the Gemini request could not be completed.',
    source: 'Fallback',
    modelUsed: 'rules-based fallback',
    generatedAt: new Date().toISOString(),
  };
}

export async function getMitigationAdvice(rawInput: MitigationInput): Promise<MitigationOutput> {
  const input = MitigationInputSchema.parse(rawInput);

  if (!hasGoogleAiKey()) {
    return buildFallbackAdvice(input);
  }

  const topWardsForPrompt = input.topWards
    .map(
      (ward, index) =>
        `${index + 1}. ${ward.wardName} (${ward.wardId}) | risk=${(ward.risk * 100).toFixed(1)}% | population=${ward.populationAffected} | trend=${ward.trend}`
    )
    .join('\n');

  const latestRunText = input.latestRun
    ? [
        `status=${input.latestRun.status}`,
        `latestPredictionDate=${input.latestRun.latestPredictionDate ?? 'n/a'}`,
        `outputRows=${input.latestRun.outputRows ?? 0}`,
        `maxRisk=${input.latestRun.maxRisk ?? 0}`,
        `meanRisk=${input.latestRun.meanRisk ?? 0}`,
        `highRiskPoints=${input.latestRun.highRiskPoints ?? 0}`,
        `mediumRiskPoints=${input.latestRun.mediumRiskPoints ?? 0}`,
        `lowRiskPoints=${input.latestRun.lowRiskPoints ?? 0}`,
      ].join(', ')
    : 'No completed pipeline run is available yet; rely on current dashboard ward metrics.';

  const prompt = `
You are Gemini acting as a municipal flood response copilot for Delhi.
You must produce grounded, practical recommendations based only on the structured telemetry below.
Do not invent external measurements. Do not mention hidden reasoning.

Current telemetry:
- City readiness score: ${input.cityReadiness}/100
- Current rainfall: ${input.rainfallMm} mm
- Weather condition: ${input.weatherCondition}
- Hotspot count: ${input.hotspotsCount}
- Average ward risk: ${input.avgRiskPercent}%
- Total population currently flagged in high-risk wards: ${input.totalPopulationAtRisk}

Top wards by current ward risk:
${topWardsForPrompt}

Latest pipeline run:
${latestRunText}

Required behavior:
- Produce an operational summary for civic authorities.
- Set escalationLevel to one of: SEVERE, ELEVATED, GUARDED, STABLE.
- Return 3 to 5 actions with realistic municipal tasks and clear rationale.
- Return 2 to 4 wardFocus entries prioritizing the most important wards.
- Give a concise 2 to 6 hour projection.
- Give a short public-facing advisory sentence.
- Ground your response in the provided metrics and mention any caveat if the latest pipeline run is missing.
- Set source to Gemini and modelUsed to the Gemini model name.
`.trim();

  try {
    const { output } = await ai.generate({
      model: googleAI.model('gemini-2.5-flash'),
      prompt,
      output: { schema: MitigationOutputSchema.omit({ source: true, modelUsed: true, generatedAt: true }) },
      config: {
        temperature: 0.2,
      },
    });

    if (!output) {
      throw new Error('Gemini returned no structured output.');
    }

    return MitigationOutputSchema.parse({
      ...output,
      source: 'Gemini',
      modelUsed: 'gemini-2.5-flash',
      generatedAt: new Date().toISOString(),
    });
  } catch (error) {
    console.warn('Gemini mitigation advisor failed, using fallback.', error);
    return buildFallbackAdvice(input);
  }
}
