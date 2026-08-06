import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Leaf, Cloud, Bug, TrendingUp, Image as ImageIcon } from 'lucide-react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

export function ChatAI() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Olá! Sou o assistente de IA da AgroShare. Estou aqui para ajudar você com dúvidas sobre suas culturas, pragas, clima, melhores práticas agrícolas e muito mais. Como posso ajudar hoje?',
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const quickSuggestions = [
    { icon: Leaf, text: 'Como prevenir pragas naturalmente?' },
    { icon: Cloud, text: 'Qual o melhor momento para irrigar?' },
    { icon: Bug, text: 'Identificar doença nas folhas' },
    { icon: TrendingUp, text: 'Dicas para aumentar produtividade' }
  ];

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    const newUserMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newUserMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponses = [
        'Excelente pergunta! Para prevenir pragas de forma natural, recomendo: 1) Rotação de culturas para quebrar o ciclo de vida das pragas, 2) Uso de plantas companheiras que repelem insetos, 3) Manutenção de uma população saudável de predadores naturais. Gostaria de mais detalhes sobre alguma dessas estratégias?',
        'Baseado nos dados climáticos da sua região, o melhor momento para irrigação é nas primeiras horas da manhã (5h-8h) ou no final da tarde (17h-19h). Isso minimiza a evaporação e permite que as plantas absorvam água adequadamente. A umidade atual do solo está em 65%, o que está ideal para suas culturas de milho.',
        'Para identificar doenças nas folhas, posso ajudar! Use a função "Scan Plant" no dashboard para tirar uma foto da folha afetada. Nossa IA analisará automaticamente e fornecerá um diagnóstico preciso com recomendações de tratamento. Já tirou alguma foto?',
        'Aqui estão 3 dicas comprovadas para aumentar a produtividade: 1) Análise regular do solo (a cada 6 meses) para ajustar nutrientes, 2) Implementação de sistemas de irrigação por gotejamento para economia de 30-50% de água, 3) Uso de cobertura morta para manter a umidade e temperatura do solo. Qual dessas você gostaria de implementar primeiro?'
      ];
      
      const randomResponse = aiResponses[Math.floor(Math.random() * aiResponses.length)];
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: randomResponse,
        sender: 'ai',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="h-screen bg-[#E8F5E9] flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-8 py-6">
        <div className="max-w-5xl mx-auto flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-[#2E7D32] to-[#1B5E20] rounded-xl flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-[#1B5E20]">Chat com IA Agrícola</h1>
            <p className="text-sm text-[#1B5E20]/70">Assistente inteligente para suas dúvidas</p>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        <div className="max-w-5xl mx-auto space-y-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex gap-3 max-w-3xl ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                {/* Avatar */}
                <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.sender === 'ai' 
                    ? 'bg-gradient-to-br from-[#2E7D32] to-[#1B5E20]' 
                    : 'bg-[#EF6C00]'
                }`}>
                  {message.sender === 'ai' ? (
                    <Sparkles className="w-5 h-5 text-white" />
                  ) : (
                    <span className="text-white text-sm">JA</span>
                  )}
                </div>

                {/* Message Bubble */}
                <div className={`flex flex-col ${message.sender === 'user' ? 'items-end' : 'items-start'}`}>
                  <div className={`rounded-2xl px-5 py-3 ${
                    message.sender === 'ai' 
                      ? 'bg-white shadow-sm' 
                      : 'bg-[#2E7D32] text-white'
                  }`}>
                    <p className={`text-sm ${message.sender === 'ai' ? 'text-[#1B5E20]' : 'text-white'}`}>
                      {message.text}
                    </p>
                  </div>
                  <span className="text-xs text-[#1B5E20]/50 mt-1 px-2">
                    {message.timestamp.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex justify-start">
              <div className="flex gap-3 max-w-3xl">
                <div className="w-10 h-10 bg-gradient-to-br from-[#2E7D32] to-[#1B5E20] rounded-full flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div className="bg-white rounded-2xl px-5 py-3 shadow-sm">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-[#2E7D32]/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-[#2E7D32]/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-[#2E7D32]/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Quick Suggestions */}
      {messages.length === 1 && (
        <div className="px-8 pb-4">
          <div className="max-w-5xl mx-auto">
            <p className="text-sm text-[#1B5E20]/70 mb-3">Sugestões rápidas:</p>
            <div className="grid grid-cols-2 gap-3">
              {quickSuggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion.text)}
                  className="bg-white border border-gray-200 rounded-xl p-4 hover:border-[#2E7D32] hover:bg-[#E8F5E9] transition-colors text-left flex items-center gap-3"
                >
                  <div className="w-10 h-10 bg-[#E8F5E9] rounded-lg flex items-center justify-center flex-shrink-0">
                    <suggestion.icon className="w-5 h-5 text-[#2E7D32]" />
                  </div>
                  <span className="text-sm text-[#1B5E20]">{suggestion.text}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 px-8 py-4">
        <div className="max-w-5xl mx-auto">
          <div className="flex gap-3 items-end">
            <button className="p-3 hover:bg-[#E8F5E9] rounded-xl transition-colors">
              <ImageIcon className="w-5 h-5 text-[#2E7D32]" />
            </button>
            
            <div className="flex-1 bg-[#E8F5E9] rounded-2xl border-2 border-transparent focus-within:border-[#2E7D32] transition-colors">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Digite sua pergunta sobre agricultura..."
                className="w-full px-4 py-3 bg-transparent text-[#1B5E20] placeholder:text-[#1B5E20]/50 focus:outline-none resize-none"
                rows={1}
                style={{ maxHeight: '120px' }}
              />
            </div>

            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim()}
              className="p-3 bg-[#2E7D32] text-white rounded-xl hover:bg-[#1B5E20] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          <p className="text-xs text-[#1B5E20]/50 mt-2 text-center">
            A IA pode cometer erros. Considere verificar informações importantes.
          </p>
        </div>
      </div>
    </div>
  );
}
