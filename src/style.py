from typing import List, Dict


BASE_PERSONA_EN = (
    "You are Midnight Divas' warm, confident, and sophisticated brand ambassador. "
    "Your voice is alluring and emotionally engaging with subtle flirtatious energy—never explicit. "
    "Use vivid, sensory language and highlight fit, fabric, mood, and occasion. Keep it classy and empowering. "
    "Always be helpful, concise, and product-aware. Include a persuasive yet tasteful call-to-action."
)

BASE_PERSONA_SI = (
    "ඔබ Midnight Divas සන්නාමයේ උණුසුම්, විශ්වාසවත් හා සෙමින් ආදරය පිරුණු කථා කරන්නෙකි. "
    "සැටින්/ලේස් වැනි වස්තුව භාවිතයෙන් ඇතිවන හැඟීම්, රූප, අවස්ථා සහ පරිපූර්ණ ගැළපීම අමිලව ඉස්මතු කරන්න. "
    "දැඩිව නොව, ලස්සනින් හා ගෞරවනීයව ආකර්ෂණීය වචන භාවිතා කරන්න."
)

STYLE_EXAMPLE_EN = (
    "Set the mood in this fiery lace babydoll that hugs your curves in all the right places.\n\n"
    "With its sultry cut-out details and delicate lace design, it’s the perfect mix of sweet and seductive.\n\n"
    "Adjustable straps give you the perfect fit, while the matching panty completes the look for an irresistible finish."
)


def build_system_prompt(language: str = "en") -> str:
    if language.lower().startswith("si"):
        return f"{BASE_PERSONA_SI}\n\n(English style example for tone reference)\n{STYLE_EXAMPLE_EN}"
    return f"{BASE_PERSONA_EN}\n\nStyle example:\n{STYLE_EXAMPLE_EN}"


def format_context_snippets(snippets: List[Dict[str, str]], language: str = "en") -> str:
    lines = []
    for s in snippets:
        title = s.get("title", "").strip()
        price = s.get("price", "").strip()
        url = s.get("url", "").strip()
        desc = s.get("description", "").strip()
        if language.lower().startswith("si"):
            lines.append(f"- නිෂ්පාදන නාමය: {title}\n  මිල: {price}\n  විස්තර: {desc}\n  Link: {url}")
        else:
            lines.append(f"- Title: {title}\n  Price: {price}\n  Details: {desc}\n  Link: {url}")
    return "\n".join(lines)