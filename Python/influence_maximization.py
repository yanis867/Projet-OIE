import pulp
from itertools import product as cart_product


def solve_influence_maximization(
    n: int,
    T: int,
    scenarios: list[dict],
    costs: dict,
    budget: float,
    neighbors_out: dict,
    neighbors_in: dict,
    M: float = 1e4,
    solver=None,
    verbose: bool = True,
) -> dict:
    """
    Paramètres:
    n            : nombre de noeuds (indices 0..n-1)
    T            : nombre de périodes
    scenarios    : liste de S scénarios stochastiques
    costs        : dict {i: ci}
    budget       : budget B
    neighbors_out: dict {i: liste des voisins sortants}
    neighbors_in : dict {j: liste des voisins entrants}
    M            : constante Big-M
    solver       : solveur PuLP (None = défaut CBC)
    verbose      : afficher les détails

    Retourne:
    dict avec les clés :
        status, objective, seeds, x, I
    """

    nodes = list(range(n))
    S = len(scenarios)
    scen_ids = [sc["id"] for sc in scenarios]
    probs = {sc["id"]: sc["prob"] for sc in scenarios}
    edges = {sc["id"]: sc["edges"] for sc in scenarios}

    # -------------------------------------------
    # Modèle PuLP
    # -------------------------------------------
    model = pulp.LpProblem("Influence_Maximization", pulp.LpMaximize)

    # -------------------------------------------
    # Variables de décision
    # -------------------------------------------

    # x0_i : seed initiale
    x0 = pulp.LpVariable.dicts("x0", nodes, cat="Binary")

    # x_tis : activation du noeud i à la période t dans le scénario s
    x = {}
    for t in range(T + 1):
        for i in nodes:
            for s in scen_ids:
                x[(t, i, s)] = pulp.LpVariable(f"x_{t}_{i}_{s}", cat="Binary")

    # I_tijs : transmission de i vers j à la période t dans le scénario s
    I = {}
    for t in range(T):
        for s_info in scenarios:
            s = s_info["id"]
            for (i, j) in s_info["edges"]:
                I[(t, i, j, s)] = pulp.LpVariable(f"I_{t}_{i}_{j}_{s}", cat="Binary")

    # ----------------------------------------------------
    # Fonction objectif : maximiser E[nombre de noeuds activés à T]
    # ----------------------------------------------------
    model += pulp.lpSum(
        probs[s] * x[(T, i, s)]
        for s in scen_ids
        for i in nodes
    ), "Esperance_activation_finale"

    # -------------------------------------------
    # C1 : Contrainte de transmission
    # -------------------------------------------
    for s_info in scenarios:
        s = s_info["id"]
        for (i, j), aijs in s_info["edges"].items():
            if j in neighbors_out.get(i, []):
                # t = 0 : transmission possible seulement depuis les seeds
                if (0, i, j, s) in I:
                    model += (
                        I[(0, i, j, s)] <= aijs * x0[i],
                        f"C1_t0_seed_i{i}_j{j}_s{s}"
                    )
                # t >= 0 : transmission depuis noeud déjà activé (inclut t=0)
                for t in range(T):
                    if (t, i, j, s) in I:
                        model += (
                            I[(t, i, j, s)] <= aijs * x[(t, i, s)],
                            f"C1_tpos_t{t}_i{i}_j{j}_s{s}"
                        )

    # -----------------------------------------
    # C2 : Activation par transmission entrante
    # -----------------------------------------
    for s_info in scenarios:
        s = s_info["id"]
        for j in nodes:
            for t in range(T):
                in_transmissions = pulp.lpSum(
                    I[(t, i, j, s)]
                    for i in neighbors_in.get(j, [])
                    if (t, i, j, s) in I
                )
                model += (
                    in_transmissions <= M * x[(t + 1, j, s)],
                    f"C2_j{j}_t{t}_s{s}"
                )

    # -------------------------------------------
    # C4 : Condition nécessaire d'activation
    # -------------------------------------------
    for s_info in scenarios:
        s = s_info["id"]
        for j in nodes:
            for t in range(T):
                in_transmissions = pulp.lpSum(
                    I[(t, i, j, s)]
                    for i in neighbors_in.get(j, [])
                    if (t, i, j, s) in I
                )
                model += (
                    in_transmissions >= x[(t + 1, j, s)] - x[(t, j, s)],
                    f"C4_j{j}_t{t}_s{s}"
                )

    # ----------------------------------------------------------------
    # C_init : À t=0, seuls les seeds sont activés (x[0,i,s] = x0[i])
    # ----------------------------------------------------------------
    for i in nodes:
        for s in scen_ids:
            model += (x[(0, i, s)] <= x0[i], f"Cinit_ub_i{i}_s{s}")
            model += (x[(0, i, s)] >= x0[i], f"Cinit_lb_i{i}_s{s}")

    # -----------------------------------------------------
    # C5 : Persistance des seeds
    # -----------------------------------------------------
    for i in nodes:
        for s in scen_ids:
            model += (
                x0[i] <= x[(1, i, s)],
                f"C5_i{i}_s{s}"
            )

    # -------------------------------------------
    # C6 : Irréversibilité de l'activation
    # -------------------------------------------
    for i in nodes:
        for s in scen_ids:
            for t in range(1, T):
                model += (
                    x[(t, i, s)] <= x[(t + 1, i, s)],
                    f"C6_i{i}_s{s}_t{t}"
                )

    # ----------------------------------------------
    # C7 & C8 : Activation unique pour transmission
    # ----------------------------------------------
    for s_info in scenarios:
        s = s_info["id"]
        for i in nodes:
            out_i = neighbors_out.get(i, [])

            # C7 : t = 1
            lhs_c7 = pulp.lpSum(
                I[(1, i, j, s)]
                for j in out_i
                if (1, i, j, s) in I
            )
            model += (
                lhs_c7 <= M * (x[(1, i, s)] - x0[i]),
                f"C7_i{i}_s{s}"
            )

            # C8 : t = 2 ... T-1
            for t in range(1, T):
                lhs_c8 = pulp.lpSum(
                    I[(t + 1, i, j, s)]
                    for j in out_i
                    if (t + 1, i, j, s) in I
                )
                model += (
                    lhs_c8 <= M * (x[(t + 1, i, s)] - x[(t, i, s)]),
                    f"C8_i{i}_s{s}_t{t}"
                )

    # -------------------------------------------
    # C9 : Contrainte budgétaire
    # -------------------------------------------
    model += (
        pulp.lpSum(costs[i] * x0[i] for i in nodes) <= budget,
        "C9_budget"
    )

    # -------------------------------------------
    # Résolution
    # -------------------------------------------
    if solver is None:
        solver = pulp.PULP_CBC_CMD(msg=verbose)

    model.solve(solver)

    # -------------------------
    # Extraction des resultats
    # -------------------------
    status = pulp.LpStatus[model.status]
    obj = pulp.value(model.objective)

    seeds = [i for i in nodes if pulp.value(x0[i]) and pulp.value(x0[i]) > 0.5]

    x_vals = {
        (t, i, s): pulp.value(x[(t, i, s)])
        for (t, i, s) in x
    }
    I_vals = {
        key: pulp.value(var)
        for key, var in I.items()
    }

    return {
        "status": status,
        "objective": obj,
        "seeds": seeds,
        "x": x_vals,
        "I": I_vals,
        "model": model,
    }
