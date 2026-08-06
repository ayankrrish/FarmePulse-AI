import { useState } from 'react';
import { Dashboard } from './components/Dashboard';
import { Diagnosis } from './components/Diagnosis';
import { Marketplace } from './components/Marketplace';
import { ChatAI } from './components/ChatAI';
import { Home, ShoppingBag, MessageSquare, User, Sprout } from 'lucide-react';

export default function App() {
  const [activeScreen, setActiveScreen] = useState<'home' | 'market' | 'chat' | 'profile' | 'diagnosis'>('home');

  return (
    <div className="min-h-screen bg-[#E8F5E9] flex">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#2E7D32] rounded-xl flex items-center justify-center">
              <Sprout className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-[#1B5E20]">AgroShare</h1>
              <p className="text-xs text-[#1B5E20]/60">Plataforma Agrícola</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4">
          <button
            onClick={() => setActiveScreen('home')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-colors mb-2 ${
              activeScreen === 'home'
                ? 'bg-[#2E7D32] text-white'
                : 'text-[#1B5E20] hover:bg-[#E8F5E9]'
            }`}
          >
            <Home className="w-5 h-5" />
            <span>Dashboard</span>
          </button>

          <button
            onClick={() => setActiveScreen('market')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-colors mb-2 ${
              activeScreen === 'market'
                ? 'bg-[#2E7D32] text-white'
                : 'text-[#1B5E20] hover:bg-[#E8F5E9]'
            }`}
          >
            <ShoppingBag className="w-5 h-5" />
            <span>Marketplace</span>
          </button>

          <button
            onClick={() => setActiveScreen('chat')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-colors mb-2 ${
              activeScreen === 'chat'
                ? 'bg-[#2E7D32] text-white'
                : 'text-[#1B5E20] hover:bg-[#E8F5E9]'
            }`}
          >
            <MessageSquare className="w-5 h-5" />
            <span>Chat com IA</span>
          </button>

          <button
            onClick={() => setActiveScreen('profile')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-colors mb-2 ${
              activeScreen === 'profile'
                ? 'bg-[#2E7D32] text-white'
                : 'text-[#1B5E20] hover:bg-[#E8F5E9]'
            }`}
          >
            <User className="w-5 h-5" />
            <span>Perfil</span>
          </button>
        </nav>

        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center gap-3 px-4 py-3">
            <div className="w-10 h-10 bg-[#2E7D32]/10 rounded-full flex items-center justify-center">
              <span className="text-[#2E7D32]">JA</span>
            </div>
            <div className="flex-1">
              <p className="text-sm text-[#1B5E20]">João Agricultor</p>
              <p className="text-xs text-[#1B5E20]/60">joão@email.com</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {activeScreen === 'home' && <Dashboard onNavigate={setActiveScreen} />}
        {activeScreen === 'diagnosis' && <Diagnosis onBack={() => setActiveScreen('home')} />}
        {activeScreen === 'market' && <Marketplace />}
        {activeScreen === 'chat' && <ChatAI />}
        {activeScreen === 'profile' && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <User className="w-20 h-20 mx-auto mb-4 text-[#2E7D32]" />
              <h2 className="text-[#1B5E20] mb-2">Perfil</h2>
              <p className="text-[#1B5E20]/70">Em desenvolvimento</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}