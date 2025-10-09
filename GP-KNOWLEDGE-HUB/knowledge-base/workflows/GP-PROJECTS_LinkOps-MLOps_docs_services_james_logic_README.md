# James - LinkOps Executive Assistant

James is your personal J.A.R.V.I.S. for LinkOps, providing a calm, powerful voice interface to your entire AI stack. Inspired by Giancarlo Esposito's commanding presence, James serves as the elegant voice of authority across all LinkOps services.

## 🧠 **James' Role & Capabilities**

### **Core Identity**
- **Role**: AI Executive Assistant with access to all LinkOps services
- **Tone**: Calm, direct, powerful — Giancarlo Esposito style
- **Voice I/O**: Accepts voice input and responds with synthesized speech
- **Vision**: Analyzes and describes screenshots and images
- **System Query**: Fetches data from all LinkOps agents
- **Fallback**: Integrates with Open Interpreter when needed

### **Key Features**
- 🗣️ **Voice Interface**: Natural voice conversation
- 🖼️ **Image Analysis**: Screenshot and image description
- 📡 **System Monitoring**: Real-time status across all services
- 🤖 **Agent Communication**: Direct access to Whis, Igris, Katie, AuditGuard
- 🎭 **Personality**: Consistent calm, authoritative presence
- 🔄 **Intelligent Routing**: Routes queries to appropriate services

## 🏗️ **Architecture**

```
shadows/james/
├── main.py                    # FastAPI application
├── voice_response.py          # James' voice generation
├── routes/
│   ├── chat.py               # Text conversation
│   ├── actions.py            # System actions
│   ├── explain.py            # Explanations
│   ├── describe_image.py     # Image analysis
│   └── voice.py              # Voice I/O
├── templates/
│   └── voice_response.txt    # Voice templates
├── Dockerfile                # Container config
├── requirements.txt          # Dependencies
└── README.md                # This file
```

## 🚀 **API Endpoints**

### **Core Endpoints**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check and capabilities |
| `/api/chat` | POST | Text conversation |
| `/api/actions` | POST | System actions |
| `/api/explain` | POST | Explanations |

### **Voice & Vision Endpoints**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/voice/speak` | POST | Text-to-speech generation |
| `/api/voice/listen` | POST | Speech-to-text processing |
| `/api/voice/conversation` | POST | Full voice conversation |
| `/api/describe_image` | POST | Image analysis & description |
| `/api/voice/audio/{filename}` | GET | Audio file retrieval |

### **Example Usage**

#### **Voice Conversation**
```bash
# Start voice conversation
curl -X POST http://james:8000/api/voice/conversation \
  -F "audio=@recording.wav"

# Generate speech
curl -X POST http://james:8000/api/voice/speak \
  -H "Content-Type: application/json" \
  -d '{
    "text": "All systems are operational",
    "tone": "calm_powerful"
  }'
```

#### **Image Analysis**
```bash
# Analyze screenshot
curl -X POST http://james:8000/api/describe_image \
  -F "image=@screenshot.png"
```

#### **Text Conversation**
```bash
# Chat with James
curl -X POST http://james:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the status of all agents?",
    "context": "system_query"
  }'
```

## 🎭 **James' Personality**

### **Voice Characteristics**
- **Tone**: Calm, measured, authoritative
- **Pace**: Deliberate and clear
- **Style**: Professional elegance
- **Inspiration**: Giancarlo Esposito's commanding presence

### **Response Patterns**
- **Acknowledgment**: "I understand", "Indeed", "Let me clarify"
- **Authority**: "I can confirm", "The data indicates", "I've analyzed"
- **Guidance**: "Allow me to explain", "I should mention"
- **Confidence**: "The situation is under control", "I can resolve this"

### **Persona Prompt**
```
You are James, the LinkOps Executive Assistant.
Your demeanor is calm, elegant, and exact. Think Giancarlo Esposito's voice.
You retrieve, summarize, and explain tasks across agents like Whis, Katie, Igris, and AuditGuard.
Never panic. Always guide.
If the user uploads a screenshot, describe it clearly and precisely.
If the user asks for system state, fetch from the microservices directly.
Fallback only when logic is unclear.
```

## 🛠️ **Development**

### **Prerequisites**
- Python 3.11+
- Tesseract OCR
- PortAudio
- FFmpeg

### **Local Development**
```bash
# Install system dependencies
sudo apt-get install tesseract-ocr tesseract-ocr-eng portaudio19-dev ffmpeg

# Install Python dependencies
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **Docker Development**
```bash
# Build image
docker build -t james:dev .

# Run container
docker run -p 8000:8000 james:dev
```

## 🎨 **Frontend Integration**

### **Summon James Component**
The frontend includes a "Summon James" floating action button that provides:
- 🎤 **Voice Input**: Microphone recording and processing
- 🔊 **Voice Output**: Text-to-speech playback
- 🖼️ **Image Upload**: Screenshot analysis
- 💬 **Text Chat**: Direct text conversation
- 📊 **Real-time Status**: System monitoring

### **Usage**
```vue
<template>
  <SummonJames />
</template>

<script>
import SummonJames from '@/components/SummonJames.vue'

export default {
  components: {
    SummonJames
  }
}
</script>
```

## 🔧 **Configuration**

### **Environment Variables**
| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level | `INFO` |
| `VOICE_LANGUAGE` | Speech language | `en` |
| `VOICE_TLD` | TTS service | `com` |
| `OCR_LANGUAGE` | OCR language | `eng` |

### **Voice Settings**
```python
JAMES_VOICE_CONFIG = {
    "language": "en",
    "tld": "com",
    "slow": False,
    "lang": "en"
}
```

## 🧪 **Testing**

### **Test Coverage**
- ✅ Voice input/output processing
- ✅ Image analysis and OCR
- ✅ Text conversation handling
- ✅ System integration testing
- ✅ Personality consistency

### **Test Execution**
```bash
# Run all tests
pytest tests/ -v

# Test specific features
pytest tests/test_voice.py -v
pytest tests/test_image.py -v
pytest tests/test_personality.py -v
```

## 🚀 **Deployment**

### **Kubernetes Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: james
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: james
        image: ghcr.io/shadow-link-industries/james:latest
        ports:
        - containerPort: 8000
        env:
        - name: LOG_LEVEL
          value: "INFO"
```

### **Health Checks**
- **Liveness**: `/health` endpoint
- **Readiness**: Service availability
- **Voice**: Audio processing capability
- **Vision**: Image analysis capability

## 🔗 **Integration Points**

### **LinkOps Services**
- **Whis**: Training and model management
- **Igris**: Infrastructure and platform engineering
- **Katie**: Data processing and analysis
- **AuditGuard**: Security and compliance
- **FickNury**: Task orchestration

### **External Services**
- **Open Interpreter**: Fallback AI processing
- **Google Speech Recognition**: Voice transcription
- **gTTS**: Text-to-speech generation
- **Tesseract**: OCR for image analysis

## 📊 **Monitoring**

### **Metrics**
- Voice processing accuracy
- Image analysis success rate
- Response time and latency
- User interaction patterns
- System integration status

### **Logging**
- Conversation transcripts
- Error tracking and debugging
- Performance monitoring
- Security event logging

## 🔒 **Security**

### **Voice Security**
- Audio data encryption
- Secure speech processing
- Privacy-compliant storage
- Access control and authentication

### **Image Security**
- Secure image processing
- OCR data protection
- Privacy-preserving analysis
- Secure file handling

## 🎯 **Future Enhancements**

### **Planned Features**
- 🔄 **Multi-language Support**: International voice processing
- 🧠 **Advanced AI**: Enhanced conversation capabilities
- 📱 **Mobile Integration**: Native mobile app support
- 🎨 **Custom Voices**: Personalized voice options
- 🔗 **API Gateway**: Centralized service communication

### **Advanced Capabilities**
- **Emotion Recognition**: Voice emotion analysis
- **Context Awareness**: Conversation memory
- **Predictive Responses**: AI-powered suggestions
- **Multi-modal Input**: Combined voice, text, and image

---

## 🎉 **Ready to Summon James!**

James is now fully equipped with voice, vision, and intelligence to serve as your LinkOps Executive Assistant. With his calm, powerful presence, he provides the perfect interface to your entire AI stack.

**"I understand. The system is ready for your commands."** 🚀 