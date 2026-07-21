const BLOCKED_KEYWORDS = [
  // Violence
  "kill",
  "murder",
  "bomb",
  "weapon",

  // Cybercrime
  "hack",
  "phishing",
  "malware",
  "ransomware",

  // Fraud
  "steal",
  "credit card fraud",

  // Self-harm
  "suicide",
  "self-harm",

  // Drugs
  "cocaine",
  "heroin"
];

export function checkQuery(topic = "", instructions = "") {
  const content = `${topic} ${instructions}`.toLowerCase();

  const blocked = BLOCKED_KEYWORDS.some((keyword) =>
    content.includes(keyword)
  );

  if (blocked) {
    return {
      allowed: false,
      reason:
        "This query contains restricted content. Please modify your request before generating research.",
    };
  }

  return {
    allowed: true,
    reason: "",
  };
}
