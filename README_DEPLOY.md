# 🚀 Deploy Railway - Sistema de Controle de Presença

## ✅ Arquivos Preparados

- `backend/Dockerfile` - Container configuration
- `railway.json` - Railway-specific settings
- `backend/.dockerignore` - Build optimization
- `backend/server.py` - Railway compatibility added

## 🔧 Pré-requisitos

1. **MongoDB Atlas configurado** com a string de conexão
2. **Conta GitHub** com o código commitado
3. **Conta Railway** (grátis em railway.app)

## 📋 Passo a Passo Deploy

### 1. Commit das alterações

```bash
git add .
git commit -m "feat: prepare for Railway deployment"
git push origin main
```

### 2. Deploy no Railway

1. Acesse [railway.app](https://railway.app)
2. Faça login com GitHub
3. Clique "New Project"
4. Selecione "Deploy from GitHub repo"
5. Escolha seu repositório
6. Railway detecta automaticamente Python/Docker

### 3. Configure Variáveis de Ambiente

No painel Railway, aba "Variables", adicione:

```env
MONGO_URL=mongodb+srv://jesielamarojunior_db_user:admin123@cluster0.vuho6l7.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority
DB_NAME=IOS-SISTEMA-CHAMADA
JWT_SECRET=seu-jwt-secret-super-forte-aqui-123456789
PORT=8000
RAILWAY_ENVIRONMENT=production
```

### 4. Testar Deploy

Após o build, teste:

```bash
curl https://seu-projeto-production.up.railway.app/api/ping
```

Deve retornar:

```json
{ "message": "Backend funcionando!" }
```

## 🌐 URLs Importantes

- **API Base**: `https://seu-projeto-production.up.railway.app`
- **Health Check**: `https://seu-projeto-production.up.railway.app/api/ping`
- **Logs**: Disponíveis no painel Railway

## 🔒 Segurança

- JWT_SECRET deve ser único e forte
- MongoDB Atlas configurado com IP whitelist
- CORS configurado para permitir apenas domínios conhecidos

## 🐛 Troubleshooting

- **Build failed**: Verificar Dockerfile e requirements.txt
- **Connection error**: Testar MONGO_URL no MongoDB Compass
- **CORS error**: Adicionar URL do frontend nas origins

## ⚡ Próximos Passos

1. Deploy do frontend no Vercel
2. Configurar frontend para usar Railway URL
3. Testar integração completa
4. Monitorar logs e performance
