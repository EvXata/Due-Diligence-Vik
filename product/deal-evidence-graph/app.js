const roles = [
  {
    role: "Analyst",
    interface: "Analyst Evidence Workbench",
    product: "Channel Economics Report",
    job: "Audit source quality, economics assumptions, and provenance before the case reaches senior review.",
    focus: ["source coverage", "unit economics", "provenance", "unvalidated claims"],
    nodes: ["evidence", "channel", "valuation", "artifact"]
  },
  {
    role: "VP/Sr Associate",
    interface: "Associate DD Workbench",
    product: "Customer Signal Intelligence",
    job: "Turn fragmented customer and market signals into a clean diligence workplan.",
    focus: ["customer pull", "adoption friction", "competitor signal", "case deltas"],
    nodes: ["customer", "claim", "risk", "artifact"]
  },
  {
    role: "Principal",
    interface: "Principal Conviction Builder",
    product: "Customer Signal Intelligence",
    job: "Build a conviction path with explicit uncertainty, refutation, and escalation gates.",
    focus: ["conviction path", "refuted hypotheses", "kill switches", "decision gates"],
    nodes: ["claim", "customer", "dissent", "risk"]
  },
  {
    role: "Partner",
    interface: "Partner Decision Brief",
    product: "Management Team Assessment",
    job: "Convert evidence into a crisp recommendation, caveats, and management read.",
    focus: ["recommendation", "team risk", "IC narrative", "client-ready brief"],
    nodes: ["management", "dissent", "valuation", "artifact"]
  },
  {
    role: "GP/MD",
    interface: "GP Portfolio Decision Console",
    product: "Management Team Assessment",
    job: "Compare this deal against portfolio exposure, manager thesis, and risk budget.",
    focus: ["portfolio impact", "team quality", "downside control", "follow-on logic"],
    nodes: ["portfolio", "management", "risk", "valuation"]
  },
  {
    role: "IC Member",
    interface: "IC Pre-read and Dissent Board",
    product: "Management Team Assessment",
    job: "Read the strongest arguments for and against the deal before voting.",
    focus: ["dissent", "vote blockers", "unresolved questions", "decision memo"],
    nodes: ["dissent", "claim", "risk", "artifact"]
  },
  {
    role: "LP/Family Office",
    interface: "LP Portfolio Lens",
    product: "Annual Portfolio Monitoring",
    job: "Monitor how deal evidence changes manager quality, concentration, and capital calls.",
    focus: ["manager signal", "portfolio drift", "risk monitoring", "annual review"],
    nodes: ["portfolio", "risk", "management", "evidence"]
  },
  {
    role: "LP/Institutional",
    interface: "Institutional LP Risk Lens",
    product: "LP Co-Investment Screening",
    job: "Screen co-investment exposure with policy-grade risk, dissent, and scenario coverage.",
    focus: ["co-investment risk", "policy fit", "scenario loss", "committee evidence"],
    nodes: ["portfolio", "dissent", "risk", "valuation"]
  },
  {
    role: "Angel",
    interface: "Angel Fast Check",
    product: "Customer Signal Intelligence",
    job: "Decide whether a deal deserves another diligence cycle without drowning in artifacts.",
    focus: ["fast yes/no", "customer pain", "valuation sanity", "next question"],
    nodes: ["customer", "valuation", "claim", "risk"]
  }
];

const deals = [
  {
    id: "cursor-19.05.2026",
    name: "Cursor",
    products: ["bear_case", "deep_audit"],
    verdict: "PASS @ $50B / CONDITIONAL @ $32-35B / PROCEED only below $25B",
    confidence: "84%",
    score: "2.4/10",
    asking: "$50B pre-money",
    fairValue: "$20-26B base / $30-35B optimistic",
    claims: [
      ["Valuation inversion", "Asking price depends on AI coding TAM expansion faster than evidence currently supports.", "watchlist"],
      ["Customer signal strength", "Adoption is strong, but enterprise durability and procurement expansion remain under-validated.", "unvalidated"],
      ["Bear case pressure", "At $50B the entry price absorbs too much future execution upside.", "validated"]
    ],
    dissent: ["What evidence proves net retention survives tool commoditization?", "What breaks if model providers bundle the workflow?", "Kill switch: no enterprise budget owner proof."]
  },
  {
    id: "dydx-19.05.2026",
    name: "dYdX",
    products: ["bear_case", "bull_case", "deep_audit"],
    verdict: "PASS",
    confidence: "82%",
    score: "1.8/10",
    asking: "$120M market cap",
    fairValue: "$29M-$85M market cap",
    claims: [
      ["Market repricing", "Current token price still exceeds risk-adjusted fair value range.", "validated"],
      ["Protocol activity", "Usage quality and fee durability require more direct verification.", "unvalidated"],
      ["Bull case containment", "Bull case does not overcome governance and liquidity risk at asking.", "refuted"]
    ],
    dissent: ["Is governance risk priced too harshly?", "What on-chain metric would reverse the pass?", "Kill switch: fee quality deteriorates for two reporting periods."]
  },
  {
    id: "tbank-24.05.2026",
    name: "T-Bank",
    products: ["bear_case", "bull_case", "deep_audit"],
    verdict: "PASS at 457.9bn / CONDITIONAL 380-450bn / PROCEED below 380bn",
    confidence: "62%",
    score: "4.2/10",
    asking: "Current MOEX market cap",
    fairValue: "380-420bn RUB base / 550-650bn red-team base",
    claims: [
      ["Regulatory discount", "Sanctions and market access issues dominate investor segmentation.", "validated"],
      ["Management execution", "Execution quality is a major positive but not enough alone for all investors.", "validated"],
      ["Investor-specific verdict", "Western and local investors need separate decision paths.", "watchlist"]
    ],
    dissent: ["Is the local-investor upside underweighted?", "Can management quality offset macro/regulatory risk?", "Kill switch: capital mobility or governance worsens."]
  },
  {
    id: "microsoft-21.05.2026",
    name: "Microsoft",
    products: ["bear_case", "deep_audit"],
    verdict: "CONDITIONAL",
    confidence: "68%",
    score: "5.4/10",
    asking: "~$470 reference",
    fairValue: "$510 base / $380-420 bear",
    claims: [
      ["AI monetization", "Base case depends on Azure/OpenAI monetization translating into durable margins.", "unvalidated"],
      ["Downside contained", "Bear case remains visible but not catastrophic at current strategic position.", "watchlist"],
      ["Hypothesis mix", "Five confirmed, four uncertain, one refuted creates conditional rather than clean pass.", "validated"]
    ],
    dissent: ["What is the first leading indicator of AI margin disappointment?", "Is the market overpaying for option value?", "Kill switch: Azure AI growth decelerates without margin lift."]
  },
  {
    id: "bitcoin-19.05.2026",
    name: "Bitcoin",
    products: ["bear_case", "deep_audit"],
    verdict: "CONDITIONAL",
    confidence: "68%",
    score: "5.8/10",
    asking: "Market entry price",
    fairValue: "Not specified",
    claims: [
      ["Macro dependency", "Case quality depends heavily on liquidity regime and risk appetite.", "watchlist"],
      ["Bear case materiality", "Downside path is credible and must be separated from structural adoption thesis.", "validated"],
      ["Evidence gap", "Fair value and buyer segmentation need stronger structured inputs.", "unvalidated"]
    ],
    dissent: ["What price invalidates the conditional view?", "Which buyer segment is the marginal validator?", "Kill switch: liquidity regime flips before thesis confirmation."]
  },
  {
    id: "tinkoff-bank-22.05.2026",
    name: "Tinkoff Bank",
    products: ["bear_case", "bull_case", "deep_audit"],
    verdict: "Conditional for Russian investor / absolute pass for Western investor",
    confidence: "67%",
    score: "5.8/10",
    asking: "Not specified",
    fairValue: "Not specified",
    claims: [
      ["Investor segmentation", "Different investor constraints create different verdicts from the same evidence.", "validated"],
      ["Access risk", "Market access and sanctions dominate fundamental analysis for Western capital.", "validated"],
      ["Valuation gap", "Fair value requires additional normalization before portfolio comparison.", "unvalidated"]
    ],
    dissent: ["Should this be one graph with two decision views?", "What protections make the local case investable?", "Kill switch: investor access worsens."]
  }
];

const graphNodes = [
  { id: "deal", type: "Deal", title: "DD deal", state: "validated", x: 42, y: 42 },
  { id: "artifact", type: "Artifact", title: "Bear / Bull / Deep Audit", state: "validated", x: 392, y: 28 },
  { id: "evidence", type: "Evidence", title: "Sources + provenance", state: "unvalidated", x: 44, y: 210 },
  { id: "claim", type: "Claim", title: "Investment hypotheses", state: "watchlist", x: 276, y: 184 },
  { id: "customer", type: "Signal", title: "Customer intelligence", state: "unvalidated", x: 520, y: 170 },
  { id: "channel", type: "Economics", title: "Channel economics", state: "unvalidated", x: 750, y: 186 },
  { id: "management", type: "Team", title: "Management assessment", state: "watchlist", x: 168, y: 378 },
  { id: "valuation", type: "Price", title: "Valuation gap", state: "validated", x: 418, y: 382 },
  { id: "risk", type: "Risk", title: "Risk register", state: "watchlist", x: 640, y: 382 },
  { id: "dissent", type: "Dissent", title: "IC objections", state: "refuted", x: 760, y: 42 },
  { id: "portfolio", type: "Portfolio", title: "LP / GP exposure", state: "watchlist", x: 810, y: 382 }
];

const edges = [
  ["deal", "artifact"],
  ["deal", "evidence"],
  ["evidence", "claim"],
  ["claim", "customer"],
  ["customer", "channel"],
  ["claim", "valuation"],
  ["valuation", "risk"],
  ["management", "risk"],
  ["risk", "dissent"],
  ["risk", "portfolio"],
  ["artifact", "dissent"]
];

const pipeline = [
  ["-1 / 0", "Onboarding and intake", "O0-O3 create Deal, Artifact, Evidence nodes from DD order and source pack."],
  ["1", "Enrichment", "Normalize company, asking price, product ordered, evidence quality, and missing fields."],
  ["2", "Market map", "Attach market/segment structure, competitor pressure, and channel economics."],
  ["3", "Customer and moat", "Route customer signal, moat, management quality, and refuted hypotheses."],
  ["4", "Growth", "Convert signals into upside, downside, future-state triggers, and monitoring hooks."],
  ["5-6", "Options and selection", "Turn graph into decision paths, kill switches, dissent, and recommendation."],
  ["7", "Delivery", "Render role-native workbenches, IC pre-read, partner brief, LP lens, and angel fast check."],
  ["8", "GTM Discovery", "Use tournament vector to identify WTP by role, product, and repeated audit need."]
];

const tests = [
  ["Localhost UI", "Static product shell is served locally with no npm dependency."],
  ["Nine interfaces", "All requested roles are selectable and update the workbench."],
  ["One graph", "Role changes highlight different nodes in the same evidence graph."],
  ["DD vector", "Eligible bear/bull/deep-audit deals populate the deal selector."],
  ["v9 mapping", "Pipeline tab maps graph execution to BCG-team v9 / Unified MAS phases."],
  ["Uncertainty visible", "Validated, unvalidated, refuted, and watchlist evidence states remain visible."]
];

let currentRole = roles[0];
let currentDeal = deals[0];

const stateClass = {
  validated: "state-validated",
  unvalidated: "state-unvalidated",
  refuted: "state-refuted",
  watchlist: "state-watchlist"
};

function init() {
  renderDeals();
  renderRoles();
  renderGraph();
  renderPipeline();
  renderTests();
  bindTabs();
  update();
}

function renderDeals() {
  const select = document.getElementById("dealSelect");
  deals.forEach((deal) => {
    const option = document.createElement("option");
    option.value = deal.id;
    option.textContent = deal.name;
    select.appendChild(option);
  });
  select.addEventListener("change", () => {
    currentDeal = deals.find((deal) => deal.id === select.value) || deals[0];
    update();
  });
}

function renderRoles() {
  const list = document.getElementById("roleList");
  roles.forEach((item) => {
    const button = document.createElement("button");
    button.className = "role-button";
    button.type = "button";
    button.dataset.role = item.role;
    button.innerHTML = `<strong>${item.role}</strong><span>${item.interface}</span>`;
    button.addEventListener("click", () => {
      currentRole = item;
      update();
    });
    list.appendChild(button);
  });
}

function renderGraph() {
  const nodeLayer = document.getElementById("graphNodes");
  nodeLayer.innerHTML = graphNodes.map((node) => `
    <article class="graph-node" data-node="${node.id}" style="left:${node.x / 9.6}%; top:${node.y / 5.6}%;">
      <span class="node-type">${node.type}</span>
      <strong class="node-title">${node.title}</strong>
      <span class="node-state ${stateClass[node.state]}">${node.state}</span>
    </article>
  `).join("");

  const edgeLayer = document.getElementById("edgeLayer");
  edgeLayer.innerHTML = edges.map(([from, to]) => {
    const source = graphNodes.find((node) => node.id === from);
    const target = graphNodes.find((node) => node.id === to);
    return `<line x1="${source.x + 76}" y1="${source.y + 41}" x2="${target.x + 76}" y2="${target.y + 41}" stroke="#c5cdc4" stroke-width="2" />`;
  }).join("");
}

function renderPipeline() {
  document.getElementById("pipelineGrid").innerHTML = pipeline.map(([phase, title, body]) => `
    <article class="pipeline-card">
      <div class="phase-index">Phase ${phase}</div>
      <strong>${title}</strong>
      <span>${body}</span>
    </article>
  `).join("");
}

function renderTests() {
  document.getElementById("testList").innerHTML = tests.map(([title, body]) => `
    <article class="test-item">
      <span class="test-dot"></span>
      <div><strong>${title}</strong><span>${body}</span></div>
    </article>
  `).join("");
}

function bindTabs() {
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tab-button").forEach((item) => item.classList.remove("is-active"));
      document.querySelectorAll(".tab-panel").forEach((item) => item.classList.remove("is-active"));
      button.classList.add("is-active");
      document.getElementById(button.dataset.tab).classList.add("is-active");
    });
  });
}

function update() {
  document.getElementById("selectedRole").textContent = currentRole.role;
  document.getElementById("interfaceTitle").textContent = currentRole.interface;
  document.getElementById("primaryProduct").textContent = currentRole.product;
  document.getElementById("roleJob").textContent = currentRole.job;
  document.getElementById("confidenceMetric").textContent = currentDeal.confidence;
  document.getElementById("gateMetric").textContent = currentRole.role.includes("LP") ? "G8" : "G7";
  document.getElementById("coverageMetric").textContent = currentDeal.products.length > 2 ? "96%" : "92%";
  document.getElementById("dealTitle").textContent = currentDeal.name;
  document.getElementById("dealVerdict").textContent = currentDeal.verdict;
  document.getElementById("dealScore").textContent = currentDeal.score;
  document.getElementById("dealAsking").textContent = currentDeal.asking;
  document.getElementById("dealFairValue").textContent = currentDeal.fairValue;

  document.querySelectorAll(".role-button").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.role === currentRole.role);
  });

  document.querySelectorAll(".graph-node").forEach((node) => {
    node.classList.toggle("is-focus", currentRole.nodes.includes(node.dataset.node));
  });

  document.getElementById("dealBadges").innerHTML = currentDeal.products.map((product) => `<span class="badge">${product}</span>`).join("");
  document.getElementById("focusBlocks").innerHTML = currentRole.focus.map((focus) => `<span class="focus-chip">${focus}</span>`).join("");
  document.getElementById("claimList").innerHTML = currentDeal.claims.map(([title, body, state]) => `
    <article class="claim">
      <strong>${title}</strong>
      <span>${body}</span>
      <span class="state ${stateClass[state]}">${state}</span>
    </article>
  `).join("");
  document.getElementById("dissentList").innerHTML = currentDeal.dissent.map((item, index) => `
    <article class="dissent">
      <strong>${index === currentDeal.dissent.length - 1 ? "Kill switch" : `Dissent ${index + 1}`}</strong>
      <span>${item}</span>
    </article>
  `).join("");
}

init();
