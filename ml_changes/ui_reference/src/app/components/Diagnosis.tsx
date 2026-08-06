import { ArrowLeft, AlertTriangle, CheckCircle, MessageCircle, Download, Share2 } from 'lucide-react';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface DiagnosisProps {
  onBack: () => void;
}

export function Diagnosis({ onBack }: DiagnosisProps) {
  return (
    <div className="min-h-screen bg-[#E8F5E9]">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-8 py-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button onClick={onBack} className="p-2 hover:bg-[#E8F5E9] rounded-xl transition-colors">
              <ArrowLeft className="w-6 h-6 text-[#1B5E20]" />
            </button>
            <div>
              <h1 className="text-[#1B5E20]">Resultado da Análise</h1>
              <p className="text-sm text-[#1B5E20]/70">Diagnóstico por Inteligência Artificial</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button className="px-4 py-2 border border-[#2E7D32] text-[#2E7D32] rounded-xl hover:bg-[#E8F5E9] transition-colors flex items-center gap-2">
              <Share2 className="w-4 h-4" />
              Compartilhar
            </button>
            <button className="px-4 py-2 border border-[#2E7D32] text-[#2E7D32] rounded-xl hover:bg-[#E8F5E9] transition-colors flex items-center gap-2">
              <Download className="w-4 h-4" />
              Exportar PDF
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-8 py-8">
        <div className="grid grid-cols-2 gap-6">
          {/* Left Column - Image & Details */}
          <div className="space-y-6">
            {/* Image Area */}
            <div className="bg-white rounded-2xl overflow-hidden shadow-sm">
              <div className="relative h-96">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1761338894194-1f3a9e73aecb?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwbGFudCUyMGRpc2Vhc2UlMjBsZWFmJTIwc3BvdHN8ZW58MXx8fHwxNzY0MDgzMTQ2fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
                  alt="Plant Analysis"
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-sm px-4 py-2 rounded-xl text-sm text-[#2E7D32] flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  Analisado
                </div>
              </div>
              <div className="p-4 border-t border-gray-200">
                <p className="text-sm text-[#1B5E20]/70">Imagem capturada em: 25 de Novembro, 2025</p>
              </div>
            </div>

            {/* Symptoms */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h3 className="text-[#1B5E20] mb-4">Sintomas Identificados</h3>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-[#2E7D32] mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm text-[#1B5E20]">Manchas amareladas nas folhas</p>
                    <p className="text-xs text-[#1B5E20]/60 mt-1">Indicativo de deficiência nutricional ou infecção fúngica</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-[#2E7D32] mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm text-[#1B5E20]">Pontos de coloração marrom</p>
                    <p className="text-xs text-[#1B5E20]/60 mt-1">Característico da fase inicial da ferrugem</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-[#2E7D32] mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm text-[#1B5E20]">Início de necrose foliar</p>
                    <p className="text-xs text-[#1B5E20]/60 mt-1">Morte de tecido vegetal nas bordas das folhas</p>
                  </div>
                </li>
              </ul>
            </div>
          </div>

          {/* Right Column - Diagnosis & Treatment */}
          <div className="space-y-6">
            {/* Diagnosis Card */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border-l-4 border-[#EF6C00]">
              <div className="flex items-start gap-4 mb-4">
                <div className="w-14 h-14 bg-[#EF6C00]/10 rounded-full flex items-center justify-center flex-shrink-0">
                  <AlertTriangle className="w-7 h-7 text-[#EF6C00]" />
                </div>
                <div className="flex-1">
                  <h2 className="text-[#1B5E20] mb-2">Ferrugem Asiática</h2>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-sm text-[#1B5E20]/70">Probabilidade:</span>
                    <span className="text-[#EF6C00]">98%</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-[#EF6C00] rounded-full" style={{ width: '98%' }}></div>
                  </div>
                </div>
              </div>

              <div className="bg-[#FFF3E0] rounded-xl p-4">
                <p className="text-sm text-[#1B5E20]">
                  A IA detectou sinais iniciais de fungos. Recomenda-se ação rápida para evitar propagação. Esta doença pode causar perdas significativas se não tratada adequadamente.
                </p>
              </div>
            </div>

            {/* Additional Info */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h3 className="text-[#1B5E20] mb-4">Informações Adicionais</h3>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-[#1B5E20]/70 mb-1">Nível de Severidade</p>
                  <div className="flex items-center gap-2">
                    <span className="px-3 py-1 bg-[#EF6C00]/10 text-[#EF6C00] rounded-full text-sm">Moderado</span>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-[#1B5E20]/70 mb-1">Risco de Propagação</p>
                  <div className="flex items-center gap-2">
                    <span className="px-3 py-1 bg-[#EF6C00]/10 text-[#EF6C00] rounded-full text-sm">Alto</span>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-[#1B5E20]/70 mb-1">Fase da Doença</p>
                  <p className="text-sm text-[#1B5E20]">Inicial - Tratamento eficaz ainda possível</p>
                </div>
              </div>
            </div>

            {/* Treatment Recommendations */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h3 className="text-[#1B5E20] mb-4">Plano de Tratamento Recomendado</h3>
              <div className="space-y-4">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-[#2E7D32] text-white rounded-full flex items-center justify-center flex-shrink-0">
                    1
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-[#1B5E20] mb-1">Isolamento Imediato</p>
                    <p className="text-xs text-[#1B5E20]/70">Isolar as plantas afetadas para evitar contaminação das culturas adjacentes</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-[#2E7D32] text-white rounded-full flex items-center justify-center flex-shrink-0">
                    2
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-[#1B5E20] mb-1">Aplicação de Tratamento</p>
                    <p className="text-xs text-[#1B5E20]/70">Aplicar tratamento orgânico com fungicida biológico (ex: Bacillus subtilis)</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-[#2E7D32] text-white rounded-full flex items-center justify-center flex-shrink-0">
                    3
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-[#1B5E20] mb-1">Monitoramento Contínuo</p>
                    <p className="text-xs text-[#1B5E20]/70">Monitorar evolução nas próximas 48-72 horas e reavaliar se necessário</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="grid grid-cols-2 gap-4">
              <button className="bg-[#2E7D32] text-white py-4 rounded-xl hover:bg-[#1B5E20] transition-colors">
                Ver Tratamento Completo
              </button>
              <button className="border-2 border-[#2E7D32] text-[#2E7D32] py-4 rounded-xl hover:bg-[#E8F5E9] transition-colors flex items-center justify-center gap-2">
                <MessageCircle className="w-5 h-5" />
                Consultar Especialista
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
