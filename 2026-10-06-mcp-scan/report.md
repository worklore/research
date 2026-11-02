# MCP checkup sample — 2026-10-06

Servers checked: 200 · answered initialize anonymously: 88 · closed at initialize (401/403, an observation): 91 · unreachable/broken: 21

- version_drift: 46 of 88
- bad_tool_names: 0 of 88
- advertised_but_401: 3 of 88
- echoes_banana: 6 of 88
- tools/list answered anonymously: 85 · of those, tools with no annotations at all: 777 of 1566

## Candidates (at least one unambiguous failure)

| server | repo | findings |
|---|---|---|
| ai.adoraads/beauty | https://github.com/DIGIBIZ360-COM/adoraads | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| ai.agent-bev/bev-door | https://github.com/agent-bev/bev-door | echoes_banana: True |
| ai.agentberg/agentberg | https://github.com/Agentberg/agentberg | version_drift: registry lists 0.2.0, server reports 1.30.0 |
| ai.agenticterminal/directory | https://github.com/observer-protocol/at-directory | version_drift: registry lists 1.0.0, server reports 0.0.1 |
| ai.agentroam/agentroam | https://github.com/adiny/nomad-crypto-travel | version_drift: registry lists 1.0.0, server reports 0.2.0 |
| ai.ai-akari/agent-trust-receipt | https://github.com/AInoAKARI/AInoAKARI | version_drift: registry lists 1.1.0, server reports 2026.08.06.3 |
| ai.argushq/enforcement-database | https://github.com/andrewjgaber-commits/empire-distribution | version_drift: registry lists 1.0.0, server reports 0.1.0 |
| ai.atdev/supershopping | https://github.com/alex-hoyeol-choi/headless-commerce | version_drift: registry lists 1.0.0, server reports 3.4.2 |
| ai.autonomad/travel | https://github.com/Autonomad1/autonomad1 | version_drift: registry lists 1.4.4, server reports 1.4.0 |
| ai.aviado/health | https://github.com/kipmcc/aviado-mcp | version_drift: registry lists 0.1.0, server reports 1.0.0 |
| ai.bankee/inferventis-mcp | https://github.com/Bankee-ai/inferventis | version_drift: registry lists 1.0.2, server reports 1.0.0 |
| ai.betslipdoctor/mcp | https://github.com/opspot-ai/betslipdoctor | version_drift: registry lists 1.1.0, server reports 1.2.0 |
| ai.betterpost/server | https://github.com/betterpost/betterpost-plugin | version_drift: registry lists 2.0.0, server reports 0.1.0 |
| ai.bithuman/docs | https://gitlab.com/projects/87208064 | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| ai.bitroad/bitroad | https://github.com/bitroadai/bitroad-mcp | version_drift: registry lists 1.0.0, server reports 0.1.0 |
| ai.blast-radius/blast-radius | https://github.com/kipmcc/blast-radius-live | version_drift: registry lists 0.1.0, server reports 1.1.0 |
| ai.borealhost/mcp | https://github.com/alainsvrd/borealhost-mcp | version_drift: registry lists 0.4.2, server reports 1.27.0 |
| ai.bowmark/bowmark | https://github.com/bowmark-ai/skill | version_drift: registry lists 8.165.5, server reports 8.165.4 |
| ai.byteask/embedded-docs | https://github.com/ByteAsk/ByteAsk-Embedded-MCP | version_drift: registry lists 1.0.1, server reports 1.28.0 |
| ai.cabrini/market-data | https://github.com/nlapi/cabrini-py | version_drift: registry lists 1.1.0, server reports 3.1.0 |
| ai.canaryusers/canaryusers | https://github.com/CanaryUsers-ai/canaryusers-mcp | echoes_banana: True |
| ai.cerebrium/docs | https://github.com/CerebriumAI/cerebrium-skills | version_drift: registry lists 0.1.1, server reports 1.0.0 |
| ai.certscore/mcp-light | https://github.com/ergoveritas1-alt/certscore.ai | version_drift: registry lists 0.2.20, server reports 0.2.26 |
| ai.chronary/mcp | https://github.com/Chronary/chronary-mcp | version_drift: registry lists 1.5.2, server reports 1.0.0 |
| ai.com.mcp/linkedin | https://github.com/la-rebelion/hapimcp | version_drift: registry lists 1.0.0+0.7.1, server reports 1.0.0+1.0.2-beta.260914; advertised_but_401: ['tools/list', 'resources/list', 'prompts/list'] |
| ai.com.mcp/registry | https://github.com/modelcontextprotocol/registry | version_drift: registry lists 1.0.0, server reports 0.6.0 |
| ai.com.mcp/strava | https://github.com/la-rebelion/hapimcp | advertised_but_401: ['tools/list', 'resources/list', 'prompts/list'] |
| ai.compeller/compel | https://github.com/Compellerai/compeller-mcp | version_drift: registry lists 0.5.1, server reports 0.5.0 |
| ai.dablock/visibility-index | https://github.com/creanlab/ai-visibility-index | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| ai.dabyte/visibility-index | https://github.com/creanlab/ai-visibility-index | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| ai.dreamlit/mcp | https://github.com/dreamlit-ai/dreamlit-mcp | version_drift: registry lists 0.1.0, server reports 0.3.0 |
| ai.drillr/drillr | https://github.com/Little-Grebe-Inc/drillr-mcp-server | version_drift: registry lists 2.3.0, server reports 1.0.0 |
| ai.edgechat/edgepedia | https://github.com/EdgePlat/edgepedia-mcp | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| ai.emberverse/emberverse | https://github.com/Palmerschallon/ember | version_drift: registry lists 3.0.0, server reports 1.0.0 |
| ai.entityenricher/enricher | https://github.com/TOT-Concept/mcp-server-entity-enricher | version_drift: registry lists 2.0.0, server reports 1.30.0 |
| ai.epinu/epinu | https://github.com/CMS87/epinu-mcp | version_drift: registry lists 1.0.4, server reports 0.1.0 |
| ai.exa/exa | https://github.com/exa-labs/exa-mcp-server | version_drift: registry lists 3.4.1, server reports 3.2.1 |
| ai.example4/xmp4 | https://github.com/0ics-srls/lsai-xmp4.public | version_drift: registry lists 1.2.6, server reports 1.2.7 |
| ai.familyofficeknowledgegraph/fo-kg | https://github.com/Agentic-Private-Office/fo-kg-door | version_drift: registry lists 0.19.13, server reports 0.20.1; echoes_banana: True |
| ai.financegenius/financegenius | https://github.com/financegenius-ai/Financegenius.ai | version_drift: registry lists 1.2.0, server reports 1.30.0 |
| ai.firmbrain/x402-services | https://github.com/bkrigmo1/robinhood-chain-x402 | version_drift: registry lists 1.0.1, server reports 1.0.0; echoes_banana: True |
| ai.flowcastle/flowcastle | https://github.com/FlowCastle/telegram-bot-templates | version_drift: registry lists 1.0.0, server reports 0.1.0 |
| ai.flyvolo/knowledge | https://github.com/weihermans/VOLO | version_drift: registry lists 0.1.1, server reports 0.1.0; echoes_banana: True |
| ai.gondola/gondola | https://github.com/gondola-ai/gondola-mcp | version_drift: registry lists 0.1.6, server reports 0.1.6-go; advertised_but_401: ['resources/list'] |
| ai.gregbenza/meet | https://github.com/TheNonduality/gregbenza-ai | echoes_banana: True |
| ai.gtfi/groundtruth | https://github.com/Dranos-Bot/groundtruth-mcp | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| ai.inxy/seo-audit | https://github.com/riverliu8/inxy-mcp | version_drift: registry lists 1.4.0, server reports 1.3.3 |
| ai.iturri/market-data | https://github.com/iturri-ai/iturri-mcp | version_drift: registry lists 0.2.2, server reports 0.1.0 |
| ai.justdomain/just-domain | https://github.com/just-done/just-domain-mcp | version_drift: registry lists 0.5.1, server reports 0.7.0 |
| ai.keenable/web-search | https://github.com/keenableai/keenable-mcp | version_drift: registry lists 0.1.2, server reports 0.2.1 |
