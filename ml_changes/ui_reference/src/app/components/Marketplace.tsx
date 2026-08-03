import { useState } from 'react';
import { Upload, Calendar, Lightbulb, TrendingUp, Users } from 'lucide-react';

export function Marketplace() {
  const [formData, setFormData] = useState({
    produto: '',
    quantidade: '',
    preco: '',
    dataColheita: ''
  });

  return (
    <div className="min-h-screen bg-[#E8F5E9]">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-8 py-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-[#1B5E20] mb-1">Nova Venda</h1>
          <p className="text-sm text-[#1B5E20]/70">Cadastre seus produtos para cooperativas e restaurantes</p>
        </div>
      </div>

      {/* Form Content */}
      <div className="max-w-7xl mx-auto px-8 py-8">
        <div className="grid grid-cols-3 gap-6">
          {/* Left Column - Form */}
          <div className="col-span-2 space-y-6">
            {/* Photo Upload */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <label className="block text-[#1B5E20] mb-3">Fotos do Produto</label>
              <div className="grid grid-cols-3 gap-4">
                <div className="border-2 border-dashed border-[#2E7D32]/30 rounded-xl p-8 text-center hover:border-[#2E7D32] transition-colors cursor-pointer bg-[#E8F5E9]/30 aspect-square flex flex-col items-center justify-center">
                  <Upload className="w-10 h-10 text-[#2E7D32] mb-2" />
                  <p className="text-sm text-[#1B5E20]/70">Adicionar foto</p>
                </div>
                <div className="border-2 border-dashed border-gray-200 rounded-xl aspect-square bg-gray-50"></div>
                <div className="border-2 border-dashed border-gray-200 rounded-xl aspect-square bg-gray-50"></div>
              </div>
              <p className="text-xs text-[#1B5E20]/60 mt-2">Adicione até 5 fotos do seu produto (JPG, PNG)</p>
            </div>

            {/* Form Fields */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h3 className="text-[#1B5E20] mb-4">Informações do Produto</h3>
              <div className="grid grid-cols-2 gap-4">
                {/* Product Dropdown */}
                <div>
                  <label className="block text-[#1B5E20] mb-2 text-sm">Produto</label>
                  <select
                    value={formData.produto}
                    onChange={(e) => setFormData({ ...formData, produto: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2E7D32] bg-white text-[#1B5E20]"
                  >
                    <option value="">Selecione o produto</option>
                    <option value="tomate">Tomate</option>
                    <option value="milho">Milho</option>
                    <option value="soja">Soja</option>
                    <option value="feijao">Feijão</option>
                    <option value="alface">Alface</option>
                    <option value="cenoura">Cenoura</option>
                    <option value="batata">Batata</option>
                    <option value="abobora">Abóbora</option>
                  </select>
                </div>

                {/* Quantity */}
                <div>
                  <label className="block text-[#1B5E20] mb-2 text-sm">Quantidade Disponível (kg)</label>
                  <input
                    type="number"
                    value={formData.quantidade}
                    onChange={(e) => setFormData({ ...formData, quantidade: e.target.value })}
                    placeholder="Ex: 500"
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2E7D32] text-[#1B5E20]"
                  />
                </div>

                {/* Price */}
                <div>
                  <label className="block text-[#1B5E20] mb-2 text-sm">Preço por kg (R$)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.preco}
                    onChange={(e) => setFormData({ ...formData, preco: e.target.value })}
                    placeholder="Ex: 4.50"
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2E7D32] text-[#1B5E20]"
                  />
                </div>

                {/* Date Picker */}
                <div>
                  <label className="block text-[#1B5E20] mb-2 text-sm">Data da Colheita</label>
                  <div className="relative">
                    <input
                      type="date"
                      value={formData.dataColheita}
                      onChange={(e) => setFormData({ ...formData, dataColheita: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2E7D32] text-[#1B5E20]"
                    />
                    <Calendar className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#2E7D32]/50 pointer-events-none" />
                  </div>
                </div>
              </div>
            </div>

            {/* Additional Details */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h3 className="text-[#1B5E20] mb-4">Detalhes Adicionais</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-[#1B5E20] mb-2 text-sm">Certificação</label>
                  <div className="flex gap-3">
                    <label className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-xl cursor-pointer hover:bg-[#E8F5E9] transition-colors">
                      <input type="checkbox" className="text-[#2E7D32]" />
                      <span className="text-sm text-[#1B5E20]">Orgânico</span>
                    </label>
                    <label className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-xl cursor-pointer hover:bg-[#E8F5E9] transition-colors">
                      <input type="checkbox" className="text-[#2E7D32]" />
                      <span className="text-sm text-[#1B5E20]">Livre de Agrotóxicos</span>
                    </label>
                    <label className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-xl cursor-pointer hover:bg-[#E8F5E9] transition-colors">
                      <input type="checkbox" className="text-[#2E7D32]" />
                      <span className="text-sm text-[#1B5E20]">Comércio Justo</span>
                    </label>
                  </div>
                </div>

                <div>
                  <label className="block text-[#1B5E20] mb-2 text-sm">Descrição do Produto</label>
                  <textarea
                    rows={4}
                    placeholder="Descreva as características do seu produto..."
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2E7D32] text-[#1B5E20] resize-none"
                  ></textarea>
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex gap-4">
              <button className="flex-1 bg-[#2E7D32] text-white py-4 rounded-xl hover:bg-[#1B5E20] transition-colors">
                Publicar Oferta
              </button>
              <button className="px-8 border-2 border-gray-200 text-[#1B5E20] py-4 rounded-xl hover:bg-white transition-colors">
                Salvar Rascunho
              </button>
            </div>
          </div>

          {/* Right Column - Insights */}
          <div className="space-y-6">
            {/* AI Suggestion */}
            <div className="bg-[#FFF3E0] border-l-4 border-[#EF6C00] rounded-2xl p-6 shadow-sm">
              <div className="flex items-start gap-3 mb-4">
                <div className="w-10 h-10 bg-[#EF6C00] rounded-full flex items-center justify-center flex-shrink-0">
                  <Lightbulb className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="text-[#1B5E20] mb-1">Dica da IA</h3>
                  <p className="text-sm text-[#1B5E20]/70">Baseado em análise de mercado</p>
                </div>
              </div>
              <div className="bg-white rounded-xl p-4">
                <p className="text-sm text-[#1B5E20] mb-2">
                  O preço médio na sua região é <span className="text-[#EF6C00]">R$ 4,50/kg</span>
                </p>
                <p className="text-xs text-[#1B5E20]/60">
                  Baseado em 23 vendas recentes de tomate orgânico
                </p>
              </div>
            </div>

            {/* Market Insights */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="w-5 h-5 text-[#2E7D32]" />
                <h3 className="text-[#1B5E20]">Demanda Atual</h3>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-[#E8F5E9] rounded-xl">
                  <span className="text-sm text-[#1B5E20]">Tomate Orgânico</span>
                  <span className="px-3 py-1 bg-[#2E7D32] text-white rounded-full text-xs">Alta</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-[#E8F5E9] rounded-xl">
                  <span className="text-sm text-[#1B5E20]">Alface</span>
                  <span className="px-3 py-1 bg-[#2E7D32] text-white rounded-full text-xs">Alta</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-xl">
                  <span className="text-sm text-[#1B5E20]">Milho</span>
                  <span className="px-3 py-1 bg-gray-300 text-gray-700 rounded-full text-xs">Média</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-xl">
                  <span className="text-sm text-[#1B5E20]">Batata</span>
                  <span className="px-3 py-1 bg-gray-300 text-gray-700 rounded-full text-xs">Média</span>
                </div>
              </div>
            </div>

            {/* Potential Buyers */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <div className="flex items-center gap-2 mb-4">
                <Users className="w-5 h-5 text-[#2E7D32]" />
                <h3 className="text-[#1B5E20]">Compradores Interessados</h3>
              </div>
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 border border-gray-200 rounded-xl">
                  <div className="w-10 h-10 bg-[#2E7D32]/10 rounded-full flex items-center justify-center">
                    <Users className="w-5 h-5 text-[#2E7D32]" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-[#1B5E20]">Cooperativa Verde</p>
                    <p className="text-xs text-[#1B5E20]/60">12 km de distância</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 border border-gray-200 rounded-xl">
                  <div className="w-10 h-10 bg-[#2E7D32]/10 rounded-full flex items-center justify-center">
                    <Users className="w-5 h-5 text-[#2E7D32]" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-[#1B5E20]">Restaurante Sabor Natural</p>
                    <p className="text-xs text-[#1B5E20]/60">8 km de distância</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 border border-gray-200 rounded-xl">
                  <div className="w-10 h-10 bg-[#2E7D32]/10 rounded-full flex items-center justify-center">
                    <Users className="w-5 h-5 text-[#2E7D32]" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-[#1B5E20]">Mercado Orgânico Central</p>
                    <p className="text-xs text-[#1B5E20]/60">15 km de distância</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="bg-white rounded-2xl p-6 shadow-sm">
              <h3 className="text-[#1B5E20] mb-4">Suas Estatísticas</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-[#1B5E20]/70">Vendas este mês</span>
                  <span className="text-[#2E7D32]">8</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-[#1B5E20]/70">Taxa de sucesso</span>
                  <span className="text-[#2E7D32]">94%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-[#1B5E20]/70">Avaliação média</span>
                  <span className="text-[#2E7D32]">⭐ 4.8</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
