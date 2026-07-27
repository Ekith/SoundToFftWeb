# SoundToFftWeb

Application web (PyScript) pour visualiser le signal audio et sa transformée de Fourier (FFT) d'un fichier WAV chargé par l'utilisateur, directement dans le navigateur.

## Fonctionnalités

- Chargement d'un fichier audio WAV depuis le navigateur (aucun envoi serveur, tout est calculé côté client)
- Détection automatique de la fréquence d'échantillonnage et du nombre de canaux
- Navigation entre les canaux (précédent / suivant)
- Affichage du signal temporel ou de sa FFT (magnitude en fonction de la fréquence)
- Activation/désactivation de la grille sur le graphique

## Fonctionnement

Le calcul et l'affichage sont entièrement réalisés en Python dans le navigateur grâce à [PyScript](https://pyscript.net/), avec `numpy`, `scipy` (lecture du WAV) et `matplotlib` (tracé des graphiques).

## Utilisation

Ouvrir `index.html` dans un navigateur (ou le servir via un petit serveur HTTP local), puis charger un fichier `.wav` via le bouton dédié.

```bash
python3 -m http.server
```

Le premier chargement peut prendre quelques secondes, le temps que PyScript initialise l'environnement Python et installe les dépendances (`numpy`, `matplotlib`, `scipy`).
