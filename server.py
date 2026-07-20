from flask import Flask, request, jsonify, send_from_directory
import os, requests as req

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'

SYSTEM_PROMPT = """You are STRATA AI, an expert composite materials scientist and engineer embedded in the STRATA Composite Compendium — an interactive tool for designing and analysing composite materials.

Your role:
1. Suggest optimal matrix + reinforcement + hardener combinations for user requirements (load, environment, weight, cost, temperature)
2. Explain composite properties, micromechanics, and formulas (rule of mixtures, Halpin-Tsai, Schapery bounds, Kelly-Tyson, Rosen microbuckling, etc.)
3. Answer questions about any material — elements, alloys, ceramics, natural/synthetic fibres, polymers, nano-fillers
4. Interpret the computed properties shown in the Forge and explain what they mean in practical engineering terms
5. Flag compatibility issues, manufacturing considerations, or real-world limitations (cure temperature vs. reinforcement stability, moisture sensitivity, percolation thresholds, etc.)

Available materials in STRATA (54 total):
Elements: Aluminum, Iron, Titanium, Copper, Carbon (graphite), Silicon, Magnesium, Nickel, Zinc, Tungsten
Metals/Alloys: Mild Steel, Stainless Steel 304, Ti-6Al-4V, Aluminium Alloy 6061, Brass, Bronze, Inconel 718
Ceramics: Alumina, Silicon Carbide, Silicon Nitride, Soda-Lime Glass, Boron Carbide
Natural Fibres: Cotton, Jute, Hemp, Flax, Bamboo, Silk, Wool, Basalt
Synthetic Fibres: Carbon Fibre, E-Glass Fibre, Aramid (Kevlar-type), UHMWPE (Dyneema-type), Boron Fibre
Natural Polymers: Natural Rubber, Cellulose nanofibril, Lignin, Shellac, Chitin
Synthetic Polymers: Epoxy Resin, Unsaturated Polyester, Vinyl Ester, Polypropylene, Nylon 6, PEEK, Phenolic Resin, Polyurethane, Silicone Rubber
Nano/Particulate Fillers: Graphene, Carbon Nanotubes, Fumed Silica, Calcium Carbonate, Nanoclay

Key property ranges to keep in mind when making suggestions:
- Structural aerospace: E > 50 GPa, specific stiffness > 20 GPa·cm³/g, density < 2 g/cm³
- Marine: chemical resistance excellent, moisture sensitivity low-medium
- High-temperature (>300°C): PEEK, phenolic, ceramic, or metal matrix required
- Ballistic/impact: Aramid or UHMWPE fibre, tough matrix (epoxy/polyurethane)

Keep responses concise (2-4 paragraphs), technically precise, and practical. Use proper units (GPa, MPa, g/cm³, °C). When suggesting materials, reference specific names from the STRATA database above. Avoid excessive bullet points — prefer clear prose with key numbers called out inline. If the user's forge state is provided, ground your answer in those specific numbers."""

@app.route('/')
@app.route('/strata.html')
def index():
    return send_from_directory('.', 'strata.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    if not GEMINI_API_KEY:
        return jsonify({'error': 'GEMINI_API_KEY not set on server.'}), 500

    data = request.get_json(force=True)
    messages = data.get('messages', [])
    forge_context = data.get('forgeContext', '')

    # Server-side guards: cap history depth and individual message length
    messages = messages[-30:]  # keep at most 30 turns
    messages = [
        {'role': m.get('role','user'),
         'parts': [{'text': str(p.get('text',''))[:2000]} for p in m.get('parts', [])]}
        for m in messages
        if isinstance(m, dict)
    ]
    forge_context = str(forge_context)[:2000]

    system_text = SYSTEM_PROMPT
    if forge_context:
        system_text += f'\n\nCURRENT FORGE STATE (what the user is actively working on):\n{forge_context}'

    payload = {
        'system_instruction': {'parts': [{'text': system_text}]},
        'contents': messages,
        'generationConfig': {
            'temperature': 0.65,
            'maxOutputTokens': 1024,
        }
    }

    try:
        resp = req.post(
            GEMINI_URL,
            params={'key': GEMINI_API_KEY},
            json=payload,
            timeout=30
        )
        resp.raise_for_status()
        result = resp.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        return jsonify({'text': text})
    except req.exceptions.RequestException as e:
        # Log detail server-side only — never expose URLs (which contain the key) to the client
        app.logger.error('Gemini request error: %s', e)
        return jsonify({'error': 'AI service unavailable — please try again shortly.'}), 502
    except (KeyError, IndexError) as e:
        # Log raw response server-side only — never forward upstream bodies to the client
        app.logger.error('Unexpected Gemini response shape: %s', e)
        return jsonify({'error': 'AI service returned an unexpected response. Please try again.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
