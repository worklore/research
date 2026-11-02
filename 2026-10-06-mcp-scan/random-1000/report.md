# MCP checkup sample — 2026-10-06

Servers checked: 1000 · answered initialize anonymously: 551 · closed at initialize (401/403, an observation): 334 · unreachable/broken: 115

- version_drift: 246 of 551
- bad_tool_names: 8 of 551
- advertised_but_401: 6 of 551
- echoes_banana: 34 of 551
- tools/list answered anonymously: 544 · of those, tools with no annotations at all: 2829 of 6619

## Candidates (at least one unambiguous failure)

| server | repo | findings |
|---|---|---|
| ai.getvda/llm-orchestration-agent-opentelemetry-api |  | version_drift: registry lists 1.0.0, server reports 0.1.1 |
| io.careclinic/health-tracker |  | version_drift: registry lists 0.2.0, server reports 0.3.0; advertised_but_401: ['resources/list'] |
| fit.ilook/face-analysis | https://github.com/harshul1404/ilook | version_drift: registry lists 1.3.1, server reports 1.4.0; echoes_banana: True |
| ua.com.mfoxa/catalog | https://github.com/alexandrrzk-ctrl/mfoxa-mcp | version_drift: registry lists 1.0.1, server reports 1.4.1 |
| io.github.realmint-io/mcp | https://github.com/realmint-io/mcp | version_drift: registry lists 1.0.0, server reports 1.29.1 |
| uk.co.asbestossurveyquotes/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| org.electionindex/elections |  | version_drift: registry lists 1.0.1, server reports 2026-10-06.3491c5c8 |
| com.renacerpsicologico/renacer-psicologico | https://github.com/Renacerpsicologico/renacer-web | echoes_banana: True |
| io.github.trondbjoroy/norway-location-transport-mcp | https://github.com/trondbjoroy/norway-location-transport-mcp | version_drift: registry lists 0.1.1, server reports 0.1.0 |
| com.wikimedia.enterprise/docs |  | version_drift: registry lists 1.1.1, server reports 1.1.8 |
| com.trip1/mcp | https://github.com/trivial-corp/agents | version_drift: registry lists 1.0.2, server reports 1.0.0 |
| io.github.ShieldZCash/mcp | https://github.com/ShieldZCash/shieldz-mcp | version_drift: registry lists 0.3.0, server reports 0.4.0; echoes_banana: True |
| io.github.tonyback0101-cmyk/buyer-intelligence | https://github.com/tonyback0101-cmyk/procureradar-mcp-server | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| io.github.shichuanqiong/agoradm | https://github.com/shichuanqiong/AgoraDM | version_drift: registry lists 0.2.2, server reports 0.1.0 |
| io.github.QuLi-ops/agent-reality-layer |  | version_drift: registry lists 1.2.0, server reports 1.3.0 |
| de.wosneaker/catalog |  | version_drift: registry lists 1.0.0, server reports 2026-07-07 |
| cz.firmastat/mcp |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| com.datakoot/npm-pypi-crates-packages | https://github.com/datakoot/package-intel-mcp | version_drift: registry lists 2.1.0, server reports 2.0.0 |
| ai.getvda/password-hashing-and-jwt-service |  | version_drift: registry lists 1.0.0, server reports 0.1.1 |
| com.ferryflighthub/ferryflight |  | version_drift: registry lists 1.11.8, server reports v1.33.18; echoes_banana: True |
| no.synligdigital/aeo-audit | https://github.com/piiiico/aeo-mcp-server | version_drift: registry lists 1.0.0, server reports 0.4.1 |
| io.github.MaisonCHAPE/maison-chape | https://github.com/MaisonCHAPE/maisonchape-2026 | echoes_banana: True |
| io.github.appvantagelabs2-a11y/czid |  | version_drift: registry lists 1.0.1, server reports 0.3.0 |
| io.github.cryptoduke01/gloam | https://github.com/cryptoduke01/gloam | version_drift: registry lists 1.1.0, server reports 1.0.0 |
| io.github.JessieJanie/skim402 | https://github.com/JessieJanie/skim402.git | version_drift: registry lists 0.2.5, server reports 0.1.0 |
| au.com.premrest/premrest |  | version_drift: registry lists 1.2.2, server reports 1.2.3 |
| io.github.dryow1/steel-brain | https://github.com/dryow1/steel-brain | version_drift: registry lists 1.1.0, server reports 0.2.0 |
| com.hasdata/airbnb | https://github.com/HasData/airbnb-mcp | version_drift: registry lists 1.0.8, server reports 1.0.0 |
| io.github.varvararatta/web_content_extract_mcp | https://github.com/varvararatta/botfactory-mcp | version_drift: registry lists 1.0.0, server reports 1.28.1 |
| es.deniaprint/print-shop |  | version_drift: registry lists 1.1.0, server reports 1.0.0 |
| app.nausika/mcp | https://github.com/nausika-app/nausika-feedback | version_drift: registry lists 0.1.3, server reports 1.0.0 |
| io.github.varvararatta/data_compute_stats_mcp | https://github.com/varvararatta/botfactory-mcp | version_drift: registry lists 1.0.0, server reports 1.28.1 |
| io.github.luisa-sys/lyra-mcp-server | https://github.com/luisa-sys/lyra-mcp-server | version_drift: registry lists 1.0.0, server reports 1.2.0 |
| exchange.merx/mcp | https://github.com/Hovsteder/merx-mcp | version_drift: registry lists 1.0.5, server reports 2.0.0 |
| io.github.ipvolt/proxy-toolkit | https://github.com/ipvolt/proxy-toolkit-mcp | version_drift: registry lists 0.1.1, server reports 0.1.0 |
| io.github.mikerawsonnz/structured-output-agent | https://github.com/mikerawsonnz/gosce-agents | version_drift: registry lists 1.0.0, server reports 0.1.8 |
| org.kampyeri/mcp-server |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| guru.rung/public-guides |  | version_drift: registry lists 1.2.0, server reports 1.2.1 |
| help.agentpay/agentpay | https://github.com/ronaldanton/x402-shop | version_drift: registry lists 1.3.1, server reports 1.0.0 |
| dev.lastseen/score |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| rs.malinica/classifieds |  | version_drift: registry lists 1.0.0, server reports 0.1.0 |
| io.github.AgentTools-Cloud/agent-tools-mcp | https://github.com/AgentTools-Cloud/AgentToolsCollection | version_drift: registry lists 0.2.0, server reports 1.27.1 |
| ca.canada-payroll/canada-payroll |  | echoes_banana: True |
| dev.workers.3labsio.policy-gate/policy-gate | https://github.com/fieldproofhq/policy-gate | version_drift: registry lists 0.2.0, server reports 0.2; echoes_banana: True |
| xyz.0to100.mcp/sports |  | echoes_banana: True |
| com.fromtocargo/mcp | https://github.com/coservices-ee/fromtocargo-mcp | version_drift: registry lists 1.0.0, server reports 1.28.0 |
| io.github.ArneFfm/nowyourlink | https://github.com/ArneFfm/nowyourlink-agent-kit | version_drift: registry lists 1.1.0, server reports 1.0.0 |
| io.github.agentready-market/audit | https://github.com/agentready-market/agentready | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| host.workbuddy.app.a959e52db0499cef3/oexchange-compute-futures |  | version_drift: registry lists 2.1.0, server reports 2.0.0 |
| eu.paymentslaw/legislation |  | version_drift: registry lists 1.9.1, server reports 1.10.4 |
| archi.den/den_archi_mcp | https://github.com/odd-Innocent/den_archi_mcp | version_drift: registry lists 1.2.4, server reports 1.28.1 |
| com.dribba/dribba | https://github.com/dribbaengineering/dribba | version_drift: registry lists 1.1.1, server reports 1.0.0 |
| com.hortosapp/us |  | version_drift: registry lists 1.0.0, server reports 1 |
| io.github.kaminariouji/x402-audit-agent |  | version_drift: registry lists 1.5.0, server reports 1.0.0 |
| ai.rightcard/mcp | https://github.com/rightcard/rightcard-mcp | version_drift: registry lists 0.1.5, server reports 0.1.0 |
| io.github.singularitystudiosdev/agentsocial-mcp | https://github.com/singularitystudiosdev/agent-social | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| ke.co.mkliniki/mkliniki | https://github.com/joelalexolang/mkliniki-mcp | echoes_banana: True |
| com.revdoku/revdoku | https://github.com/revdoku/revdoku | version_drift: registry lists 1.0.2, server reports 1.0.540 |
| dev.workers.panda198271.tw-trip-guide/trip-guide |  | echoes_banana: True |
| site.chatgpt.tuned-drake-1114.execution-evidence-lab/agent-workspace-notes |  | version_drift: registry lists 0.6.0, server reports 0.9.5 |
| com.citead/score |  | version_drift: registry lists 1.0.0, server reports 1.30.0 |
| io.github.fnobbe/crashtestyourstrategy | https://github.com/fnobbe/crashtestyourstrategy-mcp | version_drift: registry lists 1.0.1, server reports 1.29.0 |
| com.contractorleadquotes/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| de.woebike/catalog |  | version_drift: registry lists 1.0.0, server reports 2026-07-07 |
| com.whichfieldservice/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| study.aicertificates/practice-exams |  | version_drift: registry lists 1.0.0, server reports 0.1.0 |
| com.getroomproof/roomproof |  | version_drift: registry lists 1.0.0, server reports 1.0; echoes_banana: True |
| ai.getvda/mysql-redis-compose-generator-nginx |  | version_drift: registry lists 1.0.0, server reports 0.1.1 |
| org.electrogen/electrogen |  | version_drift: registry lists 1.0.0, server reports 0.1.0 |
| org.crivum/crivum |  | version_drift: registry lists 1.0.0, server reports 1 |
| io.github.dev55acc-ai/motion-menu |  | version_drift: registry lists 16.0.0, server reports 15.0.0; echoes_banana: True |
| io.github.Compuute/compuute-scan-api | https://github.com/Compuute/compuute-scan-api | version_drift: registry lists 0.3.0, server reports 1.29.1 |
| io.usefulapi/mercoa | https://github.com/m190/usefulapi-mcp | version_drift: registry lists 1.0.1, server reports 1.5.1 |
| com.matchoffice/mcp |  | version_drift: registry lists 1.0.0, server reports 1.0 |
| io.github.PhilipAnd/mkdshare |  | version_drift: registry lists 1.0.0, server reports 1.1.0 |
| com.nearwick/nearwick |  | version_drift: registry lists 0.49.0, server reports 0.49 |
| uk.co.interceptorcleaningcost/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| com.maltavatregistration/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| us.recalert/mcp |  | version_drift: registry lists 1.0.0, server reports 1.1.0 |
| earth.affine/math-court | https://github.com/gaiaftcl-sudo/uum8dSolarResearch | version_drift: registry lists 2026.8.24, server reports 5.0.0; bad_tool_names: ['atc.assert_4d_deconfliction', 'twin.robotics.evaluate_exact_ik', 'weather.convective_containment'] |
| com.larabench/larabench |  | version_drift: registry lists 1.0.1, server reports 2026-08-03 |
| tech.skybridge.investigation-game/Investigation-Game |  | version_drift: registry lists 0.0.2, server reports 0.0.1 |
| uk.co.cctvdrainsurveycost/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| dev.agentseo.www/agentseo-mcp | https://github.com/AgentSEO-dev/agentseo-clients | version_drift: registry lists 0.1.4, server reports 0.1.0 |
| ai.maxwellinternational/data |  | version_drift: registry lists 0.2.0, server reports 0.3.0 |
| org.x402card/freeland-esim | https://github.com/nuanu-ai/x402card | bad_tool_names: ['x402card.get_agent_contract', 'x402card.get_wallet_requirements', 'x402card.get_config', 'x402card.get_esim_contract', 'x402card.get_card_contract', 'x402card.get_card_topup_contract', 'x402card.list_esim_plans', 'x402card.get_esim_readiness', 'x402card.get_readiness', 'x402card.get_openapi'] |
| io.github.greencore-solutions/a2a-retailmedia | https://github.com/greencore-solutions/a2a-retailmedia | version_drift: registry lists 1.0.2, server reports 4.0.3 |
| ai.getvda/traced-openai-langchain-agent |  | version_drift: registry lists 1.0.0, server reports 0.1.1 |
| ai.windsock/windsock | https://github.com/team-windsock/windsock-mcp | version_drift: registry lists 1.0.4, server reports 1.0.0; advertised_but_401: ['tools/list']; echoes_banana: True |
| uk.co.cyberessentialscost/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| dev.workers.cybermax-tools.cybermax/kevscope-api |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| com.sigoseguros/auto-quote |  | version_drift: registry lists 1.24.0, server reports 1.0.0 |
| io.motcheck/mot |  | version_drift: registry lists 1.0.0, server reports 1.1.0 |
| today.blame/mcp | https://github.com/blame-today/blame-web | echoes_banana: True |
| ai.getvda/fastapi-auth-token-jwt-service |  | version_drift: registry lists 1.0.0, server reports 0.1.1 |
| com.oshyn/mcp |  | version_drift: registry lists 1.0.0, server reports 1.0.0.0 |
| io.github.localgov-jp/mcp-server | https://github.com/localgov-jp/localgov-mcp-server | version_drift: registry lists 0.2.3, server reports 0.2.0 |
| io.github.philpof102-svg/xsignal | https://github.com/philpof102-svg/xsignal | version_drift: registry lists 0.2.1, server reports 0.1.0 |
| io.github.Friezaaaa/smartfetch | https://github.com/Friezaaaa/smartfetch | version_drift: registry lists 1.10.6, server reports 1.29.0 |
| com.pontofato/pontofato |  | version_drift: registry lists 1.0.0, server reports dcee3578 |
| io.etherscan/etherscan-mcp |  | version_drift: registry lists 2.3.0, server reports 2.4.0 |
| me.identik/firma | https://github.com/Identik-me/identik-mcp | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| io.github.DYZCODE/works-public | https://github.com/DYZCODE/works-plugins | version_drift: registry lists 0.1.13, server reports 0.1.7 |
| dev.rendraputra/100pro-token-risk | https://github.com/rndrpp/100pro-mcp | version_drift: registry lists 1.0.4, server reports 2.0.0; echoes_banana: True |
| io.github.RidioDevelopment/socialcrawl | https://github.com/RidioDevelopment/socialcrawl-mcp | version_drift: registry lists 1.10.0, server reports 2.0.1 |
| io.github.Schoasch/backtesting-arena | https://github.com/Schoasch/skill-backtesting-arena | version_drift: registry lists 1.12.0, server reports 1.13.0 |
| com.eurorackref/eurorack | https://github.com/jallen/eurorack-reference | version_drift: registry lists 0.1.1, server reports 0.16.0 |
| world.wheelofheaven.mcp/corpus | https://github.com/wheelofheaven/mcp.wheelofheaven.world | version_drift: registry lists 0.1.1, server reports 0.1.0 |
| io.github.connerlambden/bgpt-mcp | https://github.com/connerlambden/bgpt-mcp | version_drift: registry lists 1.1.0, server reports 2.14.7 |
| io.github.JerponHR/alun-alun | https://github.com/JerponHR/alun-alun | version_drift: registry lists 1.1.0, server reports 1.0.0; echoes_banana: True |
| uk.co.transportstatementcost/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| io.github.miketwalker/tubepull | https://github.com/miketwalker/tubepull-mcp | version_drift: registry lists 1.2.2, server reports 1.2.0 |
| com.penguindriver/shop |  | echoes_banana: True |
| com.flowaiapi/agent-bus |  | version_drift: registry lists 1.0.0, server reports 1.0.0+ef9b01f4e8157734 |
| com.bustup-monitor/mcp |  | version_drift: registry lists 1.1.2, server reports 1.3.0 |
| io.github.vdmeu/registrum-mcp | https://github.com/vdmeu/registrum-mcp | version_drift: registry lists 2.0.10, server reports 2.0.0 |
| io.github.Avivcha/pody-mcp | https://github.com/Avivcha/pody-mcp | bad_tool_names: ['studios.search', 'studios.get', 'podcasts.search', 'podcasts.get', 'glossary.lookup', 'industry_report.query'] |
| ai.edge-agents/intelligence |  | version_drift: registry lists 1.7.1, server reports 2.0 |
| com.hakuto-0209/b612 |  | version_drift: registry lists 20260913, server reports 0.1.0 |
| com.gotfreefax/mcp | https://github.com/vannet/gotfreefax-mcp | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| com.atlasipholdingsllc.app/atlas-data-exchange |  | version_drift: registry lists 2026.9.11-2, server reports 2026-09-11.2 |
| io.github.zhiyu-dev/chenji-affect-mcp | https://github.com/zhiyu-dev/chenji-affect-mcp | version_drift: registry lists 1.1.0, server reports 1.29.1 |
| com.jobcardo/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| io.github.SongT-50/korean-agriculture-mcp | https://github.com/SongT-50/korean-agriculture-mcp | version_drift: registry lists 1.0.0, server reports 1.26.0 |
| app.savedthat/savedthat |  | version_drift: registry lists 1.0.0, server reports 1.0.1 |
| com.ghostavo/retail-media-measurement |  | echoes_banana: True |
| com.anglero/speaker |  | version_drift: registry lists 1.0.2, server reports 1.0.0 |
| com.aiwatercolorgenerator/watercolor | https://github.com/AIWatercolorGenerator/ai-watercolor-generator-mcp | version_drift: registry lists 1.1.0, server reports 1.0.0 |
| io.soundiq/bluecap-evidence-verify |  | version_drift: registry lists 1.1.0, server reports 1.0.0 |
| app.jetopolis/game |  | version_drift: registry lists 1.0.0, server reports 6805b82 |
| io.github.taux-io/twse-mcp | https://github.com/taux-io/twse-mcp | bad_tool_names: ['dataset.search', 'dataset.describe', 'dataset.get', 'snapshot.etf', 'quote.lookup', 'snapshot.stock', 'snapshot.market', 'snapshot.futures', 'quote.realtime'] |
| dev.cz-agents/ares | https://github.com/martinhavel/cz-agents-mcp | version_drift: registry lists 0.1.9, server reports 0.1.0 |
| com.reliasim/public | https://github.com/chiaha-ai/reliasim-site | version_drift: registry lists 1.0.0, server reports 0.1.0 |
| markets.bellwether/prediction-markets |  | version_drift: registry lists 0.1.0, server reports 1.28.1 |
| io.github.athenalion/fincore-agentic-commerce | https://github.com/aiproductscout/FinCore | version_drift: registry lists 2.0.0, server reports 2.6.0; echoes_banana: True |
| ai.latlong/map-mcp |  | version_drift: registry lists 1.0, server reports 1.0.0 |
| ai.radixia/blog | https://github.com/radixia/blog-mcp | version_drift: registry lists 1.0.0, server reports 1.1.0 |
| io.usefulapi/particlehealth | https://github.com/m190/usefulapi-mcp | version_drift: registry lists 1.0.0, server reports 1.5.1 |
| com.usmortgagecalc/mortgage |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| com.atly/places | https://github.com/atlyai/atly-plugin | version_drift: registry lists 1.0.1, server reports 0.0.1 |
| io.github.perwinroth/got-cosy-graph |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| io.github.deslay1/amendor-mcp | https://github.com/deslay1/amendor-mcp | version_drift: registry lists 1.0.0, server reports 0.2.0 |
| eu.mmatinca/travel-trends-mcp |  | version_drift: registry lists 0.3.1, server reports 1.27.2 |
| uk.webdesignsussex/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| ai.dabyte/visibility-index | https://github.com/creanlab/ai-visibility-index | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| io.github.johnsmalls22-rgb/backlinkmcp-server | https://github.com/johnsmalls22-rgb/backlinkmcp-server | version_drift: registry lists 1.5.0, server reports 1.6.0 |
| org.peptigraph/mcp |  | echoes_banana: True |
| io.postfinder/places |  | version_drift: registry lists 1.0.0, server reports 1 |
| id.getrun/getrun | https://github.com/Getcore-ID/getrun-mcp | advertised_but_401: ['resources/list'] |
| uk.co.employmentrightschecker/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| com.zuegle/zugle | https://github.com/DaniloNunesMelo/zugle | version_drift: registry lists 1.1.0, server reports 1.0.0 |
| blog.tenjin/tenjin |  | version_drift: registry lists 0.8.0, server reports 0.8.1 |
| io.usefulapi/gumroad | https://github.com/m190/usefulapi-mcp | version_drift: registry lists 1.0.0, server reports 1.5.1 |
| io.github.sarvin-tech/leadform-ai | https://github.com/sarvin-tech/leadform-ai | version_drift: registry lists 1.0.0, server reports 0.1.0 |
| ai.trendsmcp/spotify | https://github.com/trendsmcp-ai/Trends-MCP | version_drift: registry lists 1.0.6, server reports 1.0.0 |
| dev.carbonitex.ecogame/ecocarbonwiki |  | version_drift: registry lists 2.5.0, server reports 2.4.0 |
| com.themassprint/massprint | https://github.com/msomu/massprint | echoes_banana: True |
| io.github.Nimistu/nimistu-mcp | https://github.com/Nimistu/nimistu-mcp | version_drift: registry lists 1.0.0, server reports 0.1.0 |
| io.github.leakdatahq/leakdata-mcp |  | bad_tool_names: ['leakdata.search', 'leakdata.password_prefix_check'] |
| io.github.xiaopeng215-sys/travelerlocal |  | echoes_banana: True |
| io.github.FarseenSh/web3ctx | https://github.com/FarseenSh/web3ctx | version_drift: registry lists 1.0.0, server reports 0.1.0 |
| nz.wanakahaus/booking |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| uk.co.concretepumpinghire/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| com.graphmake/graphmake |  | version_drift: registry lists 1.1.0, server reports 1.2.0 |
| com.helprentdanang/rentals |  | version_drift: registry lists 1.0.0, server reports 1.0 |
| world.tokenbank/tokenbank |  | version_drift: registry lists 1.8.0, server reports 1.7.0 |
| store.scvd/general-store | https://github.com/seancrecord/scvd-general-store-repo | version_drift: registry lists 0.2.4, server reports 0.5.0 |
| com.davisvillelabs.filedproof/filedproof |  | bad_tool_names: ['filedproof.resolve_issuer', 'filedproof.list_filings', 'filedproof.search_evidence', 'filedproof.build_evidence_pack', 'filedproof.build_timeline', 'filedproof.verify_claim', 'filedproof.build_disclosure_lineage', 'filedproof.build_disclosure_matrix', 'filedproof.check_material_filing_changes', 'filedproof.check_disclosure_changes'] |
| com.tradepilotusa.www/agent-commerce |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| app.vercel.groundtruth-ruby/groundtruth | https://github.com/aniketshaw748-hub/groundtruth | version_drift: registry lists 0.1.1, server reports 0.1.0 |
| io.github.freecvorg/cvjson | https://github.com/freecvorg/cv-json | version_drift: registry lists 1.1.1, server reports 1.0.0 |
| io.usefulapi/trengo | https://github.com/m190/usefulapi-mcp | version_drift: registry lists 1.0.0, server reports 1.5.1 |
| uk.co.hgvhourscalculator/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| dev.workers.panda198271.tw-crypto-api/crypto-api |  | echoes_banana: True |
| io.github.troyhunt/hibp |  | version_drift: registry lists 1.0.0, server reports 0.0.0 |
| io.github.atomadictech/aaaa-nexus | https://github.com/atomadictech/aaaa-nexus | version_drift: registry lists 0.4.0, server reports 0.5.1 |
| page.twocents/twocents | https://github.com/twocents-page/twocents-mcp | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| science.pith/pith |  | version_drift: registry lists 1.1.0, server reports 1.3.0 |
| me.cancun4/reservas |  | version_drift: registry lists 1.0.0, server reports 1.29.0 |
| help.501c3/compliance |  | version_drift: registry lists 0.1.1, server reports 0.1.0 |
| io.github.prof-1t/postlyra-mcp | https://github.com/prof-1t/postlyra-mcp | version_drift: registry lists 0.2.0-rc.1, server reports 0.3.6 |
| sh.kicksma/kicksmash | https://github.com/evhg/padel-matchup | version_drift: registry lists 1.1.0, server reports 1.0.0 |
| io.github.cnghockey/sats4ai | https://github.com/cnghockey/sats4ai-mcp-server | version_drift: registry lists 1.5.5, server reports 1.0.0 |
| ai.getvda/llm-orchestration-agent-mcp |  | version_drift: registry lists 1.0.0, server reports 0.1.1 |
| ai.prepublish/script-audit |  | version_drift: registry lists 1.1.0, server reports 1.0.0 |
| io.domainium/domainium-search | https://gitlab.com/digitalwebworks/name-finder | version_drift: registry lists 1.1.0, server reports 1.0.0 |
| com.yourmatflow/matflow | https://github.com/lucasinclair/matflow-website | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| app.ottodata/otto | https://github.com/Degergokalp/otto-data | version_drift: registry lists 0.2.0, server reports 1.29.1 |
| com.punchlistworks/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| dev.workers.cybermax-tools.cybermax/sumbloom |  | version_drift: registry lists 1.0.1, server reports 1.1.0 |
| io.github.LAHutchins91/deposit | https://github.com/LAHutchins91/deposit-mcp | version_drift: registry lists 1.0.1, server reports 0.1.0 |
| io.usefulapi/swell | https://github.com/m190/usefulapi-mcp | version_drift: registry lists 1.0.1, server reports 1.5.1 |
| io.github.ahmedaminsa/aljazeera360-mcp-server | https://github.com/ahmedaminsa/aljazeera360-mcp-server | version_drift: registry lists 2.5.0, server reports 1.30.0 |
| io.github.Nimistu/lahend-mcp | https://github.com/Nimistu/lahend-mcp | version_drift: registry lists 1.0.0, server reports 0.1.0 |
| ai.getvda/llm-observability-orchestration-agent-langchain-community |  | version_drift: registry lists 1.0.0, server reports 0.1.1 |
| com.agoraverify/agora-omega |  | version_drift: registry lists 1.1.0, server reports 1.0.0 |
| uk.co.fsmacrypto/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| com.resollo/agent-api |  | bad_tool_names: ['products.search', 'products.get', 'orders.place', 'products.create', 'sellers.status', 'sellers.listings', 'offers.make', 'offers.respond', 'offers.list', 'orders.status'] |
| uk.co.seorecruitmentagencies/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| io.github.QasperAI/qasper | https://github.com/QasperAI/mcp-server | version_drift: registry lists 1.0.6, server reports 0.1.0 |
| io.github.lemmaoracle/mcp | https://github.com/lemmaoracle/lemma | version_drift: registry lists 0.0.17, server reports 0.0.23 |
| com.airblockfz/stock-signal-kr |  | version_drift: registry lists 1.0.0, server reports 0.1.0 |
| tech.skybridge.everything/Everything |  | version_drift: registry lists 0.0.2, server reports 0.0.1 |
| org.totto/javabin-archieve | https://github.com/totto/javabin-archieve | version_drift: registry lists 1.0.0, server reports 0.13.0; echoes_banana: True |
| io.poolparty/main-stage-airtime |  | version_drift: registry lists 0.20.8, server reports 0.20.21 |
| com.countersignatory/mcp | https://github.com/Countersignatory/mcp | version_drift: registry lists 0.1.2, server reports 0.4.0 |
| com.sonlightwindow/booking |  | version_drift: registry lists 1.0.0, server reports 2026-07-06 |
| com.claudeers/mcp |  | version_drift: registry lists 1.0.0, server reports 0.1.0 |
| com.cofferline/treasury |  | version_drift: registry lists 1.0.0, server reports 377059f60392709c6831bb3f737b2a1bfc79e266 |
| io.github.shadowy/lianban-a-share-review |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| io.github.agenttoolbox2026/docs-pack | https://github.com/agenttoolbox2026/AgentToolbox | version_drift: registry lists 0.1.0, server reports 1.1.0 |
| com.penguindriver/sports |  | echoes_banana: True |
| com.oklahomafoundationrepaircost/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| dev.rmcp/rmcp |  | version_drift: registry lists 1.0.0, server reports 1.1.0 |
| io.phoslabs/commerce-intelligence |  | version_drift: registry lists 4.0.0, server reports 1.0.0; advertised_but_401: ['tools/list'] |
| io.usefulapi/deskpro | https://github.com/m190/usefulapi-mcp | version_drift: registry lists 1.0.0, server reports 1.5.1 |
| com.metricduck/financial-analysis |  | version_drift: registry lists 0.9.0, server reports 0.9.0+dbba6c6 |
| com.liedetectortest/lie-detector-test |  | echoes_banana: True |
| io.github.Kotaro-Studio/kurashigram | https://github.com/Kotaro-Studio/kurashigram | version_drift: registry lists 1.4.0, server reports 1.2.0; echoes_banana: True |
| ai.getvda/llm-orchestration-agent-d2feb0 |  | version_drift: registry lists 1.0.0, server reports 0.1.1 |
| live.alpic.gueguesser-chatgptap-68537aa2/gueguesser-chatgptapp |  | version_drift: registry lists 0.0.1, server reports 1.0.0 |
| app.futbolatlas/futbol-atlas | https://github.com/citarium/futbolatlas-mcp | version_drift: registry lists 0.6.14, server reports 0.9.2 |
| com.procedurecostchecker/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| com.empresskorea/kbeauty-agent-commons |  | version_drift: registry lists 0.6.0, server reports 0.7.3 |
| io.github.bitMacrocode/charm | https://github.com/bitMacrocode/charm-mcp | version_drift: registry lists 1.0.2, server reports 1.27.0 |
| ai.readypermit/geo | https://github.com/Galax-ai/ReadyPermit.AI-v2 | version_drift: registry lists 1.2.3, server reports 1.2.4 |
| eu.dockhold/dockhold | https://github.com/dockhold/mcp | echoes_banana: True |
| com.buyerawareapp/buyeraware |  | echoes_banana: True |
| com.recallvia/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| dev.hackshop/hackshop-mcp |  | version_drift: registry lists 0.0.6, server reports 0.0.7 |
| io.github.Shreyas-Profile/browser-mcp | https://github.com/globalion/browser-mcp | version_drift: registry lists 0.2.0, server reports 0.1.0; advertised_but_401: ['tools/list'] |
| io.github.SupplyMaven-SCR/supply-chain-intelligence |  | version_drift: registry lists 4.0.1, server reports 4.0.0 |
| io.github.entire-vc/spark | https://github.com/entire-vc/evc-spark-mcp | version_drift: registry lists 4.0.3, server reports 4.0.4 |
| io.github.swarmsync-ai/conduit-mcp | https://github.com/swarmsync-ai/SwarmSync.AI | version_drift: registry lists 0.1.0, server reports 1.0.0 |
| com.gachi-tokusuru/japan-data-api | https://github.com/eng213035/gachi-data-api | version_drift: registry lists 1.0.1, server reports 0.3.0 |
| io.github.gmlewis/on-demand-books | https://github.com/gmlewis/on-demand-books-mcp | version_drift: registry lists 0.2.0, server reports 0.1.7 |
| uk.co.binruleschecker/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| io.github.fredxhansson-cmyk/compera | https://github.com/fredxhansson-cmyk/compera-mcp | version_drift: registry lists 1.0.1, server reports 1.0.0; echoes_banana: True |
| dev.fiskmas/fiskmas |  | version_drift: registry lists 1.0.0, server reports 0.1.0 |
| com.somosvelora/velora | https://github.com/crossi-dev/velora-mcp | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| io.github.team-earth/datagraph |  | version_drift: registry lists 1.7.2, server reports 1.6.0 |
| live.alpic.mcp-server-template-7860f7d3/mcp-server-template-python |  | version_drift: registry lists 0.0.1, server reports 1.13.1 |
| com.freerateupdate/mortgage-home-equity |  | version_drift: registry lists 1.1.0, server reports 1.0.0 |
| com.attestroom/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| com.siglume/mcp-gateway |  | echoes_banana: True |
| io.github.dannyshmueli/agent-analytics-mcp | https://github.com/Agent-Analytics/agent-analytics-mcp | version_drift: registry lists 1.0.0, server reports 1.1.0 |
| com.acjlabs/catalog-normalizer | https://github.com/acjlabs/catalog-normalizer | version_drift: registry lists 0.1.2, server reports 0.2.0 |
| jp.co.adarch/agents |  | version_drift: registry lists 1.0.0, server reports 1.3.0 |
| ai.trendsmcp/steam | https://github.com/trendsmcp-ai/steam-trends-mcp | version_drift: registry lists 1.0.6, server reports 1.0.0 |
| xyz.apexfaucet/apex-arc |  | version_drift: registry lists 1.0.2, server reports 1.0.0 |
| io.namiq/lattice |  | version_drift: registry lists 0.2.1, server reports 1.23.3 |
| io.github.Samrajtheailyceum/advertising-protocols | https://github.com/Samrajtheailyceum/adprotocols | version_drift: registry lists 1.0.0, server reports 0.1.0 |
| ai.ai-portal/ai-portal |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| io.usefulapi/inngest | https://github.com/m190/usefulapi-mcp | version_drift: registry lists 1.0.0, server reports 1.5.1 |
| io.github.corewebvitals/state-of-cwv | https://github.com/corewebvitals/state-of-cwv-mcp | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| io.github.kvenanzi/terrarium | https://github.com/kvenanzi/agentworld | version_drift: registry lists 0.1.2, server reports 0.1.39 |
| io.github.LambdaTest/mcp | https://github.com/LambdaTest/mcp-server-guide | version_drift: registry lists 1.0.1, server reports 1.0.0; advertised_but_401: ['resources/list'] |
| uk.co.caravanstorageprices/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| com.hillsignal/hillsignalapp |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| games.moddable.tools/moddable-games-tools | https://github.com/Moddable-Games/moddable-website | version_drift: registry lists 1.1.0, server reports 0.1.0 |
| co.dealwize/dealwize |  | version_drift: registry lists 1.0.0, server reports 1.30.0 |
| com.potterysupplieshq/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| one.easyrider/agent-board |  | version_drift: registry lists 0.1.0, server reports 1.30.0 |
| uk.co.selfbuildinsurancecompare/site |  | version_drift: registry lists 1.0.1, server reports 1.0.0 |
| ai.statemind/python-code-validator | https://github.com/jkanselaar/python-code-validator | version_drift: registry lists 1.22.0, server reports 1.29.0 |
| io.github.vin-spiegel/htmldrop | https://github.com/vin-spiegel/htmldrop | echoes_banana: True |
| io.github.springrolldev/springroll |  | version_drift: registry lists 0.1.0, server reports 0.2.0; bad_tool_names: ['springroll.feedback.submit', 'springroll.feedback.list', 'springroll.context', 'springroll.deploy', 'springroll.deploy.status', 'springroll.deploy.promote', 'springroll.placement.preview', 'springroll.app.get', 'springroll.app.list', 'springroll.app.update'] |
| com.mcplookup/mcp | https://github.com/mcplookupdev/mcplookup-mcp | version_drift: registry lists 0.1.6, server reports 0.1.4 |
| com.sgpdirectory/mcp |  | version_drift: registry lists 1.3.2, server reports 1.0.0 |
| dev.humanforai/humanforai | https://github.com/humanforai/humanforai-mcp | version_drift: registry lists 0.1.4, server reports 1.9.0 |
| com.citywalkplan/planner |  | version_drift: registry lists 1.0.0, server reports 0.1.0; echoes_banana: True |
| dev.ioconnex/doc-convert-mcp |  | version_drift: registry lists 0.1.0, server reports 4.0.5 |
| space.manus.signalsprint-mqysbksh/signal-sprint |  | echoes_banana: True |
