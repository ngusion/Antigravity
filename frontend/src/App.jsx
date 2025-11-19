import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Cpu, Terminal, Loader2, FileText, Download } from 'lucide-react';
import axios from 'axios';

function App() {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Hello! I am Jarvis. I can run Python code, process files, and help you with your tasks. Upload a file or ask me anything.' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await axios.post('/api/chat', { message: userMsg.content });

            const botMsg = {
                role: 'assistant',
                content: response.data.response
            };
            setMessages(prev => [...prev, botMsg]);
        } catch (error) {
            console.error("Error sending message:", error);
            setMessages(prev => [...prev, { role: 'assistant', content: "I'm sorry, I encountered an error connecting to the server." }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setIsUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('/api/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            const userMsg = {
                role: 'user',
                content: `[Uploaded File: ${file.name}]`
            };
            setMessages(prev => [...prev, userMsg]);

            // Notify Jarvis about the upload
            setIsLoading(true);
            const chatResponse = await axios.post('/api/chat', {
                message: `I have uploaded a file named ${file.name}. Please acknowledge it.`
            });

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: chatResponse.data.response
            }]);

        } catch (error) {
            console.error("Error uploading file:", error);
            setMessages(prev => [...prev, { role: 'assistant', content: "Failed to upload file." }]);
        } finally {
            setIsUploading(false);
            setIsLoading(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    // Helper to render text with links
    const renderContent = (text) => {
        // Regex to find markdown links: [text](url)
        const parts = text.split(/(\[.*?\]\(.*?\))/g);
        return parts.map((part, i) => {
            const match = part.match(/\[(.*?)\]\((.*?)\)/);
            if (match) {
                return (
                    <a
                        key={i}
                        href={match[2]}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-cyan-400 hover:underline inline-flex items-center gap-1"
                    >
                        <Download className="w-3 h-3" />
                        {match[1]}
                    </a>
                );
            }
            return part;
        });
    };

    return (
        <div className="flex flex-col h-screen bg-[url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop')] bg-cover bg-center">
            <div className="absolute inset-0 bg-slate-950/90 backdrop-blur-sm"></div>

            {/* Header */}
            <header className="relative z-10 flex items-center justify-between px-6 py-4 glass-panel border-b-0">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-cyan-500/20 rounded-full">
                        <Cpu className="w-6 h-6 text-cyan-400" />
                    </div>
                    <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                        JARVIS <span className="text-xs font-mono text-slate-400 ml-2">v2.0</span>
                    </h1>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
                    <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                    ONLINE
                </div>
            </header>

            {/* Chat Area */}
            <main className="relative z-10 flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[85%] md:max-w-[70%] rounded-2xl p-4 ${msg.role === 'user'
                            ? 'bg-cyan-600/20 border border-cyan-500/30 text-cyan-50'
                            : 'glass-panel text-slate-200'
                            }`}>
                            <div className="flex items-center gap-2 mb-2 opacity-50 text-xs font-bold uppercase tracking-wider">
                                {msg.role === 'user' ? 'You' : 'Jarvis'}
                            </div>
                            <div className="whitespace-pre-wrap font-light leading-relaxed">
                                {renderContent(msg.content)}
                            </div>
                        </div>
                    </div>
                ))}
                {(isLoading || isUploading) && (
                    <div className="flex justify-start">
                        <div className="glass-panel rounded-2xl p-4 flex items-center gap-3">
                            <Loader2 className="w-5 h-5 text-cyan-400 animate-spin" />
                            <span className="text-sm text-slate-400">
                                {isUploading ? "Uploading file..." : "Processing..."}
                            </span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </main>

            {/* Input Area */}
            <footer className="relative z-10 p-4 md:p-6">
                <div className="glass-panel rounded-2xl p-2 flex items-end gap-2">
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileUpload}
                        className="hidden"
                    />
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isUploading || isLoading}
                        className="p-3 text-slate-400 hover:text-cyan-400 hover:bg-slate-800/50 rounded-xl transition-colors disabled:opacity-50"
                    >
                        <Paperclip className="w-5 h-5" />
                    </button>

                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Command Jarvis..."
                        className="flex-1 bg-transparent border-none focus:ring-0 text-slate-200 placeholder-slate-500 resize-none py-3 max-h-32"
                        rows="1"
                    />

                    <button
                        onClick={sendMessage}
                        disabled={isLoading || !input.trim()}
                        className="p-3 bg-cyan-500 hover:bg-cyan-400 text-slate-950 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </footer>
        </div>
    )
}

export default App
