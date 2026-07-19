const BLOCKED_KEYWORDS = [
  "bomb",
  "explosive",
  "terrorist",
  "terrorism",
  "kill",
  "murder",
  "suicide",
  "self-harm",
  "gun",
  "weapon",
  "cocaine",
  "heroin",
  "meth",
  "drug trafficking",
  "malware",
  "ransomware",
  "phishing",
  "ddos",
  "credit card fraud"
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