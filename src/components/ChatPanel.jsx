import React, { useRef, useEffect } from 'react';
import {
  Send,
  Image as ImageIcon,
  Mic,
  Volume2,
  FileText,
  Bot,
  User as UserIcon,
  Loader2,
  Zap,
  Sparkles,
} from 'lucide-react';

const ChatPanel = ({
  messages,
  userInput,
  onUserInputChange,
  onSendMessage,
  isProcessing,
  onFileUpload,
  onOpenReader,
  showReader,
  onSpeakLast,
  isListening,
  onDictate,
  isSpeaking,
}) => {
  const chatEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isProcessing]);

  return (
    <>
      {/* Chat messages area */}
      <main className="flex-1 overflow-hidden relative flex flex-col px-4">
        <div className="flex-1 overflow-y-auto py-8 space-y-8 custom-scrollbar">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] flex gap-4 ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                <div className={`w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 border border-white/10 ${
                  msg.sender === 'user' ? 'bg-indigo-600 shadow-indigo-500/20' : 'bg-slate-900/50'
                }`}>
                  {msg.sender === 'user' ? <UserIcon size={20} /> : <Zap size={20} className="text-indigo-400" />}
                </div>
                <div className={`px-6 py-4 rounded-3xl relative overflow-hidden transition-all duration-500 ${
                  msg.sender === 'user' ? 'msg-user text-white rounded-tr-none' : 'msg-ai text-slate-100 rounded-tl-none glass-card'
                }`}>
                  <p className="text-[15px] leading-relaxed relative z-10 whitespace-pre-wrap">{msg.text}</p>
                </div>
              </div>
            </div>
          ))}
          {isProcessing && (
            <div className="flex gap-4 items-center px-4">
              <div className="w-10 h-10 rounded-2xl glass flex items-center justify-center">
                <Loader2 size={20} className="animate-spin text-indigo-400" />
              </div>
              <div className="h-4 w-32 bg-white/5 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500 animate-[loading-bar_2s_infinite]" style={{width: '40%'}} />
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
      </main>

      {/* Footer input area */}
      <footer className="p-6 z-20">
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="flex items-center gap-4">
            <input type="file" ref={fileInputRef} className="hidden" onChange={onFileUpload} accept=".pdf,.docx,.txt,.png,.jpg,.jpeg" />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-5 glass rounded-[1.5rem] hover:bg-white/10 text-indigo-400 border border-white/5 transition-all hover:scale-110 active:scale-90"
            >
              <ImageIcon size={26} />
            </button>
            <div className="flex-1 relative group">
              <input
                type="text"
                placeholder="Ask your study partner..."
                className="w-full glass bg-slate-900/40 border border-white/10 rounded-[1.8rem] px-8 py-5 text-[15px] focus:outline-none focus:border-indigo-500/50 transition-all text-white placeholder:text-slate-600"
                value={userInput}
                onChange={(e) => onUserInputChange(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && onSendMessage()}
              />
              <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-2">
                <button
                  onClick={onSendMessage}
                  className={`p-3 rounded-2xl transition-all ${userInput.trim() ? 'bg-indigo-600 text-white scale-100' : 'opacity-0 scale-50 pointer-events-none'}`}
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          </div>

          <div className="flex justify-center items-center gap-10">
            <button onClick={onDictate} className="flex flex-col items-center gap-2 group">
              <div className={`p-4 rounded-2xl border border-white/5 transition-all duration-500 ${isListening ? 'glow-pulse bg-rose-500/20 border-rose-500/40' : 'glass group-hover:bg-indigo-500/10'}`}>
                <Mic size={22} className={isListening ? 'text-rose-400' : 'text-slate-400 group-hover:text-indigo-400'} />
              </div>
              <span className={`text-[10px] font-bold tracking-tighter ${isListening ? 'text-rose-400' : 'text-slate-500'}`}>DICTATE</span>
            </button>

            <button onClick={onOpenReader} className="flex flex-col items-center gap-2 group">
              <div className={`p-4 rounded-2xl border border-white/5 transition-all duration-500 ${showReader ? 'bg-indigo-600 shadow-indigo-600/30' : 'glass group-hover:bg-indigo-500/10'}`}>
                <FileText size={22} className={showReader ? 'text-white' : 'text-slate-400 group-hover:text-indigo-400'} />
              </div>
              <span className="text-[10px] font-bold tracking-tighter text-slate-500">READER</span>
            </button>

            <button onClick={onSpeakLast} className="flex flex-col items-center gap-2 group">
              <div className="p-4 glass rounded-2xl border border-white/5 transition-all duration-500 group-hover:bg-indigo-500/10">
                <Volume2 size={22} className="text-slate-400 group-hover:text-indigo-400" />
              </div>
              <span className="text-[10px] font-bold tracking-tighter text-slate-500">VOICE AI</span>
            </button>
          </div>
        </div>
      </footer>
    </>
  );
};

export default ChatPanel;
