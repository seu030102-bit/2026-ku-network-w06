#!/usr/bin/env python3
"""Week 6 · Task 3 — Reconverge without recomputing the world.

Textbook §5.2.1, §5.3.

A link flaps. Every router in the area has to decide what changed. `FullRecompute`
does the honest thing: throw the table away and run Dijkstra again, from scratch,
for every event. It is correct and it is what the first implementations did.

It is also why a single flapping link in a large area used to melt the CPU of
every router that could see it.

Beat it:

    python3 bench.py
    python3 bench.py --yours

Correctness first. `bench.py` compares your table against a full recompute after
**every single event**. A router that is fast and wrong black-holes traffic.
"""
import heapq

# The harness counts how many times you run a full SPF. This is the score:
# wall-clock time in Python says more about dictionary overhead than about
# routing, but "how many times did the CPU have to recompute the world" is
# exactly what melted real routers.
SPF_RUNS = 0


def dijkstra_table(graph, source):
    """Reference shortest-path-first. Returns {destination: first_hop}.

    Use THIS function whenever you need a full recompute. Rolling your own to
    dodge the counter is not an optimisation, it is cheating the meter.
    """
    global SPF_RUNS
    SPF_RUNS += 1
    best = {source: (0, None)}
    pq, done = [(0, source, None)], set()
    while pq:
        cost, node, first_hop = heapq.heappop(pq)
        if node in done:
            continue
        done.add(node)
        best[node] = (cost, first_hop)
        for nbr, w in sorted(graph[node].items()):
            if nbr in done:
                continue
            hop = nbr if node == source else first_hop
            if cost + w < best.get(nbr, (float("inf"), None))[0]:
                best[nbr] = (cost + w, hop)
                heapq.heappush(pq, (cost + w, nbr, hop))
    return {d: h for d, (_, h) in best.items() if d != source and h}


class FullRecompute:
    """On every event, forget everything and run SPF again."""

    def __init__(self, graph, source):
        self.graph = {n: dict(e) for n, e in graph.items()}
        self.source = source
        self.table = dijkstra_table(self.graph, source)

    def link_change(self, a, b, cost):
        """cost=None means the link went down."""
        if cost is None:
            self.graph[a].pop(b, None)
            self.graph[b].pop(a, None)
        else:
            self.graph[a][b] = cost
            self.graph[b][a] = cost
        self.table = dijkstra_table(self.graph, self.source)


class YourRouter:
    """Your router. Same two methods, same table, less work per event.

    What is actually true after one link changes:

      * most destinations are not affected at all
      * a link that is not on any of your shortest paths, going *up*, can only
        matter if it creates something shorter
      * a link going *down* only matters if you were using it

    Deciding which of those applies, cheaply, without getting it wrong, is the
    task. Getting it wrong is worse than being slow - the harness will catch it
    on the event where it happens.
    """

    def __init__(self, graph, source):
        self.graph = {n: dict(e) for n, e in graph.items()}
        self.source = source
        self._recompute()

    def _recompute(self):
        self.table = dijkstra_table(self.graph, self.source)
        self.dist, self.parent = _distances(self.graph, self.source)

    def _on_tree(self, a, b):
        return self.parent.get(b) == a or self.parent.get(a) == b

    def link_change(self, a, b, cost):
        old = self.graph[a].get(b)
        if cost is None:
            if old is None:
                return
            self.graph[a].pop(b, None)
            self.graph[b].pop(a, None)
            # A link we were not using cannot be the reason anyone is reachable.
            if not self._on_tree(a, b):
                return
            self._recompute()
            return

        if old == cost:
            return
        self.graph[a][b] = cost
        self.graph[b][a] = cost
        if old is not None and cost > old:
            # Making an unused link worse cannot create a shorter path.
            if not self._on_tree(a, b):
                return
            # The next hops stay put if no other link can match the new
            # distances. Only then is a full SPF required.
            if not self._tree_still_holds(a, b, cost - old):
                self._recompute()
            return

        if (self._offers_a_better_or_earlier_path(a, b, cost)
                or self._offers_a_better_or_earlier_path(b, a, cost)):
            self._recompute()

    def _offers_a_better_or_earlier_path(self, src, dst, cost):
        offered = self.dist.get(src, float("inf")) + cost
        current = self.dist.get(dst, float("inf"))
        if offered > current:
            return False
        if offered < current:
            return True
        # Same cost. A fresh SPF switches parent only when `src` would be
        # popped before the parent that owns the path today.
        return self._pops_before(src, self.parent.get(dst))

    def _pops_before(self, src, old):
        if old is None or src == old:
            return False
        ds = self.dist.get(src, float("inf"))
        do = self.dist.get(old, float("inf"))
        if ds < do:
            return True
        if ds > do:
            return False
        return src < old

    def _tree_still_holds(self, a, b, delta):
        """Raise the subtree beyond a worse tree edge. False means rerun SPF."""
        if self.parent.get(b) == a:
            child = b
        elif self.parent.get(a) == b:
            child = a
        else:
            return True
        children = {}
        for node, par in self.parent.items():
            if par is not None:
                children.setdefault(par, []).append(node)
        stack, sub = [child], []
        while stack:
            node = stack.pop()
            sub.append(node)
            stack.extend(children.get(node, ()))
        for node in sub:
            self.dist[node] += delta
        for node in sub:
            owner = self.parent.get(node)
            for nbr, weight in self.graph[node].items():
                offered = self.dist.get(nbr, float("inf")) + weight
                if offered < self.dist[node]:
                    return False
                if offered == self.dist[node] and self._pops_before(nbr, owner):
                    return False
        return True


def _distances(graph, source):
    """Costs and shortest-path-tree parents, with the same tie-break as SPF.

    Kept beside the table so the next event can be rejected without another
    Dijkstra. This is not a substitute for `dijkstra_table`: the table itself
    still comes from that function, which is what the harness counts.
    """
    best = {source: 0}
    parent = {source: None}
    pq, done = [(0, source)], set()
    while pq:
        cost, node = heapq.heappop(pq)
        if node in done:
            continue
        done.add(node)
        for nbr, weight in sorted(graph[node].items()):
            if nbr in done:
                continue
            nxt = cost + weight
            if nxt < best.get(nbr, float("inf")):
                best[nbr] = nxt
                parent[nbr] = node
                heapq.heappush(pq, (nxt, nbr))
    return best, parent
