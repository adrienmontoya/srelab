# Runbook — Panne PostgreSQL

## Déclencheurs
- Alerte `HighErrorRate` sur `/items` (taux d'erreur > 1%)
- Logs applicatifs : `connection refused` ou `could not connect to server`
- Dashboard Grafana : pic du taux d'erreur 5xx

## Étapes de résolution

### 1. Confirmer l'alerte
```bash
kubectl get pods | grep postgres
```
Observer le statut : `CrashLoopBackOff`, `Error`, ou pod absent.

### 2. Collecter les logs
```bash
kubectl logs deployment/postgres --tail=50
```
Chercher : OOMKilled, config error, disk full.

### 3. Redémarrer le pod
```bash
kubectl delete pod -l app=postgres
```
Le Deployment recrée automatiquement un pod sain.

### 4. Vérifier le retour en service
```bash
kubectl get pods -w
curl http://localhost:8000/health
curl http://localhost:8000/items
```
Les erreurs 5xx doivent disparaître dans Grafana.

### 5. Analyser la cause racine
- Vérifier les ressources : `kubectl describe pod -l app=postgres`
- Vérifier la variable DATABASE_URL dans le Deployment
- Vérifier l'espace disque du nœud Kind

### 6. Post-mortem
- Noter la durée d'impact
- Identifier la cause (OOM, config, réseau)
- Mettre à jour ce runbook si nécessaire

## Rollback
Si le problème persiste après redémarrage :
```bash
kubectl rollout undo deployment/postgres
```
