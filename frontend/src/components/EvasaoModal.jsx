import React, { useState, useEffect } from 'react';
import { X, AlertTriangle } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Textarea } from './ui/textarea';
import { listarMotivosEvasao, registrarEvasao } from '@/lib/api';
import { toast } from 'sonner';

const EvasaoModal = ({ aluno, aberto, onFechar, onSucesso }) => {
  const [motivos, setMotivos] = useState([]);
  const [motivoSelecionado, setMotivoSelecionado] = useState('');
  const [observacao, setObservacao] = useState('');
  const [carregando, setCarregando] = useState(false);
  const [carregandoMotivos, setCarregandoMotivos] = useState(true);

  useEffect(() => {
    if (aberto) {
      carregarMotivos();
      setMotivoSelecionado('');
      setObservacao('');
    }
  }, [aberto]);

  const carregarMotivos = async () => {
    try {
      setCarregandoMotivos(true);
      const data = await listarMotivosEvasao();
      setMotivos(data);
    } catch (error) {
      console.error('Erro ao carregar motivos:', error);
      toast.error('Erro ao carregar motivos de evasão');
    } finally {
      setCarregandoMotivos(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!motivoSelecionado) {
      toast.error('Selecione um motivo de evasão');
      return;
    }

    try {
      setCarregando(true);
      
      await registrarEvasao({
        id_aluno: aluno.id,
        motivo: motivoSelecionado,
        observacao: observacao || null
      });

      toast.success('Evasão registrada com sucesso');
      onSucesso();
      onFechar();
    } catch (error) {
      console.error('Erro ao registrar evasão:', error);
      toast.error('Erro ao registrar evasão');
    } finally {
      setCarregando(false);
    }
  };

  return (
    <Dialog open={aberto} onOpenChange={onFechar}>
      <DialogContent className="sm:max-w-[600px]" data-testid="evasao-modal">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <AlertTriangle className="w-6 h-6 text-orange-500" />
            Registrar Evasão
          </DialogTitle>
          <DialogDescription>
            {aluno && (
              <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-700">
                  <strong>Aluno:</strong> {aluno.nome}
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Presença Atual:</strong> {aluno.presenca_total}%
                </p>
              </div>
            )}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          {/* Motivo da Evasão */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">
              Motivo da Evasão <span className="text-red-500">*</span>
            </label>
            <Select 
              value={motivoSelecionado} 
              onValueChange={setMotivoSelecionado}
              disabled={carregandoMotivos}
            >
              <SelectTrigger className="w-full" data-testid="motivo-select">
                <SelectValue placeholder="Selecione o motivo" />
              </SelectTrigger>
              <SelectContent>
                {motivos.map((m) => (
                  <SelectItem key={m.value} value={m.value}>
                    {m.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Observação */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">
              Observações (opcional)
            </label>
            <Textarea
              value={observacao}
              onChange={(e) => setObservacao(e.target.value)}
              placeholder="Adicione informações adicionais sobre a evasão..."
              rows={4}
              className="w-full"
              data-testid="observacao-textarea"
            />
          </div>

          {/* Aviso */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <p className="text-xs text-yellow-800">
              <strong>Atenção:</strong> Ao registrar a evasão, o status do aluno será alterado para "Desistente" e não poderá ser revertido facilmente.
            </p>
          </div>

          {/* Botões */}
          <div className="flex justify-end gap-3 pt-4">
            <Button 
              type="button" 
              variant="outline" 
              onClick={onFechar}
              disabled={carregando}
            >
              Cancelar
            </Button>
            <Button 
              type="submit" 
              disabled={carregando || !motivoSelecionado}
              data-testid="submit-evasao-btn"
            >
              {carregando ? 'Registrando...' : 'Registrar Evasão'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default EvasaoModal;
