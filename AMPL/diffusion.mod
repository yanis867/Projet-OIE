# Maximisation de la diffusion d informations sur un reseau social
# Modele MILP stochastique - Theme 17 OIE M1 SID

# --- PARAMETRES ---
param n integer;        # nombre de noeuds du reseau
param T integer;        # nombre de periodes de diffusion
param S integer;        # nombre de scenarios stochastiques
param M := 100;         # constante Big-M

param pi{1..S};                            # probabilite du scenario s
param c{1..n} >= 0;                        # cout d activation du noeud i comme seed
param B >= 0;                              # budget total disponible
param a{1..n, 1..n, 1..S} binary default 0; # 1 si lien i->j actif dans scenario s

# --- VARIABLES DE DECISION ---
var x0{1..n} binary;                       # 1 si noeud i choisi comme seed (t=0)
var x{1..n, 1..T, 1..S} binary;            # 1 si noeud i actif a t dans scenario s
var I{1..n, 1..n, 0..T-1, 1..S} binary;   # 1 si noeud i transmet a j a t dans s

# --- FONCTION OBJECTIF ---
maximize obj :
    sum{s in 1..S} pi[s] * sum{i in 1..n} x[i, T, s];

# --- CONTRAINTES ---

# C1 : Transmission a t=0 uniquement depuis les seeds
s.t. C1{i in 1..n, j in 1..n, s in 1..S} :
    I[i, j, 0, s] <= a[i, j, s] * x0[i];

# C1b : Transmission a t>0 uniquement depuis noeuds deja actifs
s.t. C1b{i in 1..n, j in 1..n, t in 1..T-1, s in 1..S} :
    I[i, j, t, s] <= a[i, j, s] * x[i, t, s];

# C2 : Si transmission arrive en j a t, alors j est active a t+1
s.t. C2{j in 1..n, t in 0..T-2, s in 1..S} :
    sum{i in 1..n} a[i, j, s] * I[i, j, t, s] <= M * x[j, t+1, s];

# C4init : Condition necessite d activation a t=1 (depuis seeds x0)
s.t. C4init{j in 1..n, s in 1..S} :
    sum{i in 1..n} a[i, j, s] * I[i, j, 0, s] >= x[j, 1, s] - x0[j];

# C4 : Condition necessite d activation a t>=2 (utilise x[j,t-1,s])
s.t. C4{j in 1..n, t in 2..T, s in 1..S} :
    sum{i in 1..n} a[i, j, s] * I[i, j, t-1, s] >= x[j, t, s] - x[j, t-1, s];

# C5 : Persistance des seeds
s.t. C5{i in 1..n, s in 1..S} :
    x0[i] <= x[i, 1, s];

# C6 : Irreversibilite de l activation
s.t. C6{i in 1..n, t in 1..T-1, s in 1..S} :
    x[i, t, s] <= x[i, t+1, s];

# C7 : Transmission unique a t=1 (depuis seeds)
s.t. C7{i in 1..n, s in 1..S} :
    sum{j in 1..n} I[i, j, 1, s] <= M * (x[i, 1, s] - x0[i]);

# C8 : Transmission unique a t>=2
s.t. C8{i in 1..n, t in 2..T-1, s in 1..S} :
    sum{j in 1..n} I[i, j, t, s] <= M * (x[i, t, s] - x[i, t-1, s]);

# C9 : Contrainte budgetaire
s.t. C9 :
    sum{i in 1..n} c[i] * x0[i] <= B;