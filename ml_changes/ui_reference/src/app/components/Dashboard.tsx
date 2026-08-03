import { Bell, Sun, Cloud, Sprout, TrendingUp, Users, Camera, Calendar, Droplets, Wind } from 'lucide-react';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface DashboardProps {
  onNavigate: (screen: string) => void;
}

export function Dashboard({ onNavigate }: DashboardProps) {
  return (
    <div className="min-h-screen bg-[#E8F5E9]">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-8 py-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-[#1B5E20] mb-1">Olá, João</h1>
            <p className="text-sm text-[#1B5E20]/70">Bem-vindo de volta à sua fazenda</p>
          </div>
          <button className="relative p-3 hover:bg-[#E8F5E9] rounded-xl transition-colors">
            <Bell className="w-6 h-6 text-[#1B5E20]" />
            <span className="absolute top-2 right-2 w-2.5 h-2.5 bg-[#EF6C00] rounded-full"></span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-8 py-8">
        <div className="grid grid-cols-3 gap-6">
          {/* Left Column - Main Content */}
          <div className="col-span-2 space-y-6">
            {/* Status Card */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h2 className="text-[#1B5E20] mb-4">Minha Plantação</h2>
              
              <div className="grid grid-cols-2 gap-6">
                <div className="relative h-64 rounded-xl overflow-hidden">
                  <ImageWithFallback
                    src="https://images.unsplash.com/photo-1609130855718-882c8515f8e7?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb3JuJTIwZmllbGQlMjBmYXJtfGVufDF8fHx8MTc2NDA4MzE0NXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
                    alt="Corn Field"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
                  <div className="absolute bottom-4 left-4 text-white">
                    <div className="flex items-center gap-2 mb-1">
                      <Sprout className="w-5 h-5" />
                      <span>Milho</span>
                    </div>
                    <p className="text-sm opacity-90">Área: 10 hectares</p>
                  </div>
                </div>

                <div className="flex flex-col justify-center space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-[#1B5E20]/70">Progresso da Colheita</span>
                      <span className="text-[#2E7D32]">80%</span>
                    </div>
                    <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                      <div className="h-full bg-[#2E7D32] rounded-full" style={{ width: '80%' }}></div>
                    </div>
                  </div>

                  <div className="bg-[#E8F5E9] rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Calendar className="w-4 h-4 text-[#2E7D32]" />
                      <span className="text-sm text-[#1B5E20]">Colheita Prevista</span>
                    </div>
                    <p className="text-[#2E7D32]">15 dias</p>
                    <p className="text-xs text-[#1B5E20]/60 mt-1">Dezembro 10, 2025</p>
                  </div>

                  <button
                    onClick={() => onNavigate('diagnosis')}
                    className="bg-[#EF6C00] text-white py-3 rounded-xl hover:bg-[#EF6C00]/90 transition-colors flex items-center justify-center gap-2"
                  >
                    <Camera className="w-5 h-5" />
                    Scan Plant
                  </button>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div>
              <h3 className="text-[#1B5E20] mb-4">Ações Rápidas</h3>
              <div className="grid grid-cols-4 gap-4">
                <button className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-all hover:scale-105">
                  <div className="w-12 h-12 bg-[#E8F5E9] rounded-xl flex items-center justify-center mb-3 mx-auto">
                    <Sprout className="w-6 h-6 text-[#2E7D32]" />
                  </div>
                  <p className="text-center text-[#1B5E20] text-sm">Meus Cultivos</p>
                </button>

                <button className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-all hover:scale-105">
                  <div className="w-12 h-12 bg-[#E8F5E9] rounded-xl flex items-center justify-center mb-3 mx-auto">
                    <Cloud className="w-6 h-6 text-[#2E7D32]" />
                  </div>
                  <p className="text-center text-[#1B5E20] text-sm">Previsão do Tempo</p>
                </button>

                <button className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-all hover:scale-105">
                  <div className="w-12 h-12 bg-[#E8F5E9] rounded-xl flex items-center justify-center mb-3 mx-auto">
                    <TrendingUp className="w-6 h-6 text-[#2E7D32]" />
                  </div>
                  <p className="text-center text-[#1B5E20] text-sm">Finanças</p>
                </button>

                <button className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-all hover:scale-105">
                  <div className="w-12 h-12 bg-[#E8F5E9] rounded-xl flex items-center justify-center mb-3 mx-auto">
                    <Users className="w-6 h-6 text-[#2E7D32]" />
                  </div>
                  <p className="text-center text-[#1B5E20] text-sm">Comunidade</p>
                </button>
              </div>
            </div>

            {/* Production Overview */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h3 className="text-[#1B5E20] mb-4">Visão Geral da Produção</h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-[#E8F5E9] rounded-xl p-4">
                  <p className="text-sm text-[#1B5E20]/70 mb-1">Cultivos Ativos</p>
                  <p className="text-2xl text-[#2E7D32]">4</p>
                </div>
                <div className="bg-[#E8F5E9] rounded-xl p-4">
                  <p className="text-sm text-[#1B5E20]/70 mb-1">Área Total</p>
                  <p className="text-2xl text-[#2E7D32]">28 ha</p>
                </div>
                <div className="bg-[#E8F5E9] rounded-xl p-4">
                  <p className="text-sm text-[#1B5E20]/70 mb-1">Produção Estimada</p>
                  <p className="text-2xl text-[#2E7D32]">15t</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Weather & Info */}
          <div className="space-y-6">
            {/* Weather Widget */}
            <div className="bg-[#2E7D32] text-white rounded-2xl p-6 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h3>Clima Atual</h3>
                <Sun className="w-8 h-8" />
              </div>
              <p className="text-4xl mb-2">28°C</p>
              <p className="text-sm opacity-90 mb-4">Ensolarado</p>
              
              <div className="space-y-2 pt-4 border-t border-white/20">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <Droplets className="w-4 h-4" />
                    <span>Umidade</span>
                  </div>
                  <span>65%</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <Wind className="w-4 h-4" />
                    <span>Vento</span>
                  </div>
                  <span>12 km/h</span>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-white/20">
                <p className="text-sm opacity-90 mb-2">Próximos 3 dias</p>
                <div className="flex justify-between">
                  <div className="text-center">
                    <Sun className="w-5 h-5 mx-auto mb-1" />
                    <p className="text-xs opacity-90">Qua</p>
                    <p className="text-sm">30°</p>
                  </div>
                  <div className="text-center">
                    <Cloud className="w-5 h-5 mx-auto mb-1" />
                    <p className="text-xs opacity-90">Qui</p>
                    <p className="text-sm">26°</p>
                  </div>
                  <div className="text-center">
                    <Sun className="w-5 h-5 mx-auto mb-1" />
                    <p className="text-xs opacity-90">Sex</p>
                    <p className="text-sm">29°</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Alerts */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h3 className="text-[#1B5E20] mb-4">Alertas</h3>
              <div className="space-y-3">
                <div className="bg-[#FFF3E0] border-l-4 border-[#EF6C00] rounded-lg p-3">
                  <p className="text-sm text-[#1B5E20]">Risco de geada amanhã</p>
                  <p className="text-xs text-[#1B5E20]/60 mt-1">Proteja as culturas sensíveis</p>
                </div>
                <div className="bg-[#E8F5E9] border-l-4 border-[#2E7D32] rounded-lg p-3">
                  <p className="text-sm text-[#1B5E20]">Irrigação recomendada</p>
                  <p className="text-xs text-[#1B5E20]/60 mt-1">Baixa umidade do solo</p>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h3 className="text-[#1B5E20] mb-4">Atividade Recente</h3>
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-[#2E7D32] rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="text-sm text-[#1B5E20]">Análise de solo concluída</p>
                    <p className="text-xs text-[#1B5E20]/60">Há 2 horas</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-[#2E7D32] rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="text-sm text-[#1B5E20]">Nova venda registrada</p>
                    <p className="text-xs text-[#1B5E20]/60">Há 5 horas</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-gray-300 rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="text-sm text-[#1B5E20]">Irrigação automática ativada</p>
                    <p className="text-xs text-[#1B5E20]/60">Ontem</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
