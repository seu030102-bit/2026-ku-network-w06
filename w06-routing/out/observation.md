## Task 1

Equal-cost paths keep the one discovered first. Neighbours are scanned in sorted name order, and a later path replaces it only when the cost is strictly smaller. A real router often installs every equal path (ECMP) or breaks the tie by the lowest next-hop router-id. This table pins a single hop, so the discovery order is the tie-break.

`u` sends `w` via `x`, not via `w`. The direct link costs 5 and `u-x-y-w` costs 3. After `u-x` fails, `v` stays on `v`. The other four move: `w` goes out the direct link, and `x`, `y`, and `z` go via `v`.

같은 비용의 경로는 먼저 발견된 것을 유지한다. 이웃은 이름순으로 보고, 나중 경로는 비용이 엄격히 더 작을 때만 바꿔 치운다. 실제 라우터는 같은 비용의 경로를 모두 넣거나(ECMP), 다음 홉의 라우터 ID가 더 작은 쪽을 고른다. 이 표는 홉을 하나로 고정하므로, 발견 순서가 타이브레이크다.

`u`는 `w`를 `w`가 아니라 `x`로 보낸다. 직통 링크는 비용 5이고 `u-x-y-w`는 3이다. `u-x`가 끊기면 `v`는 그대로 `v`다. 나머지 넷은 바뀐다. `w`는 직통 링크로 나가고, `x`, `y`, `z`는 `v`를 거친다.

## Task 2

The domestic trace leaves the private campus at hop 3, `163.152.233.129`. Hop 1 is `172.16.0.2` and hop 2 is `192.168.98.132`; both are still private. After hop 3 every answering router is in `163.152`, and `163.152.6.10` itself never answered within 15 hops. The Stanford trace reaches the provider at hop 4, `175.121.235.141`, then only `10.x` addresses. There is no hostname and no stable jump of about 100 ms, so no cable can be named from it. `1.1.1.1` is approached at hop 12, `141.101.82.12`, at about 70 ms, after the Korean hops `39.120.253.58` and `211.45.68.85`. That replica is off this LAN. A line of `* * *` is a router that does not send ICMP Time Exceeded. A hop that answers one probe and stars the others is rate limiting. Those are different failures.

Three FRR routers on this PC confirmed the protocol, not a classmate's file. Docker Hub has no `frrouting/frr:v9.1.0`, so the image was `quay.io/frrouting/frr:10.4.5`. Before the cut each router held the subnet it is not attached to: r1 had `172.21.0.0/16` via both r2 and r3, r2 had `172.18.0.0/16` via both, r3 had `172.20.0.0/16` via both. The r1-r2 interface was eth0 in this run. `show ip ospf interface` read Hello 10s, Dead 40s. `frr.conf` does not set either; the running interface does.

Shutting that interface moved r1's and r2's tables by the first sample, 1.85 s later. r2's route to `172.18.0.0/16` kept only the via-r3 next hop, while neighbor 1.1.1.1 was still Full with about 30 s of dead time left. The 40 s timer did not move the table. r1 saw its own port go down and the new LSA came around r3. The neighbor was Full again 1.97 s after the port came back, because a hello is sent rather than waited for. A later run, with interface names matching `frr.conf`, raised r1 `eth0` (toward r3, `172.18.0.0/16`) from cost 10 to 100. Both neighbors stayed Full, so the link did not go down. The tables are `out/route-cost-before.txt` and `out/route-cost-after.txt`. Before, r2 reached `172.18.0.0/16` at cost 20 via both r1 (`172.20.0.3`) and r3 (`172.21.0.2`). After 1.64 s only the via-r3 hop remained. r1's table moved as well: `172.21.0.0/16` dropped the via-r3 hop, and `172.18.0.0/16` left the cost-100 connected route for the path via r2 at cost 30. A cost change is only that LSA. A failure that left the interface up would still have to burn the dead interval before anyone noticed.

국내 경로는 홉 3 `163.152.233.129`에서 사설 캠퍼스를 나간다. 홉 1은 `172.16.0.2`, 홉 2는 `192.168.98.132`이고 둘 다 아직 사설이다. 홉 3 이후 응답한 라우터는 모두 `163.152` 안이고, `163.152.6.10` 자신은 15홉 안에 답하지 않았다. 스탠퍼드 경로는 홉 4 `175.121.235.141`에서 사업자에 닿은 뒤 `10.x`만 나온다. 호스트 이름도 없고 약 100 ms가 안정적으로 뛰는 구간도 없어서, 이 트레이스만으로 해저 케이블을 지목할 수 없다. `1.1.1.1`은 홉 12 `141.101.82.12`에서 약 70 ms로 다가오고, 그 앞에 국내 홉 `39.120.253.58`, `211.45.68.85`가 있다. 그 복제본은 이 LAN 위가 아니다. `* * *` 한 줄은 ICMP Time Exceeded를 보내지 않는 라우터다. 프로브 하나만 답하고 나머지는 별인 홉은 속도 제한이다. 둘은 다른 실패다.

FRR 라우터 세 대를 이 PC에서 띄웠다. 같은 반의 파일이 아니다. Docker Hub에 `frrouting/frr:v9.1.0`이 없어서 이미지는 `quay.io/frrouting/frr:10.4.5`였다. 끊기 전에 각 라우터는 자기가 붙어 있지 않은 서브넷을 갖고 있었다. r1은 `172.21.0.0/16`을 r2와 r3 둘 다로, r2는 `172.18.0.0/16`을 둘 다로, r3은 `172.20.0.0/16`을 둘 다로 가지고 있었다. 이번 실행에서 r1-r2 인터페이스는 eth0였다. `show ip ospf interface`는 Hello 10초, Dead 40초였다. `frr.conf`는 둘 다 적지 않고, 돌고 있는 인터페이스가 그 값을 보여 줬다.

그 인터페이스를 내리자 r1과 r2의 표는 첫 표본에서 이미 바뀌어 있었고, 시각은 1.85초 뒤였다. r2가 `172.18.0.0/16`으로 가는 길에서 r1을 지나는 다음 홉은 빠지고 r3만 남았는데, 이웃 1.1.1.1은 아직 Full이었고 dead 시간이 약 30초 남아 있었다. 40초 타이머가 표를 옮긴 것이 아니다. r1은 자기 포트가 내려간 것을 봤고, 새 LSA가 r3을 돌아 왔다. 포트를 다시 올리자 그 이웃은 1.97초 만에 다시 Full이 됐다. 돌아오는 쪽은 hello를 보내고, 기다리는 침묵이 아니다. 나중 실행에서는 인터페이스 이름이 `frr.conf`와 같았다. r1의 `eth0`(r3 쪽, `172.18.0.0/16`) 비용을 10에서 100으로 올렸다. 이웃 둘은 Full인 채로 남아서 링크는 내려가지 않았다. 표는 `out/route-cost-before.txt`와 `out/route-cost-after.txt`에 있다. 전에는 r2가 `172.18.0.0/16`에 비용 20으로 r1(`172.20.0.3`)과 r3(`172.21.0.2`) 둘 다로 갔다. 1.64초 뒤에는 r3 경유만 남았다. r1의 표도 움직였다. `172.21.0.0/16`에서 r3 경유가 빠졌고, `172.18.0.0/16`은 비용 100인 연결 경로 대신 r2를 거치는 비용 30 경로로 바뀌었다. 비용 변경은 그 LSA뿐이다. 인터페이스가 살아 있는 장애라면, 누군가 알아채기 전에 여전히 dead 간격을 태워야 한다.

## Task 3

`YourRouter` keeps, between events, the distance and the parent of every reachable router, plus the forwarding table. That is one number and one name per router, 400 of them here.

A link that is not on that tree can fail or get worse with no SPF. A shorter link, a tie that would be popped earlier, and a tree link that fails or gets worse when some other link can match the new distance, still run a full SPF. Those are the 329 runs, 67% fewer than 1001, with no wrong table. The grade is good. It is short of the 75% line.

Wall time went the other way: 3.23 s against the baseline's 1.96 s. The extra time is Python walking the parent lists. A router is short of control-plane CPU when one flap makes every router recompute, which is the 1001 runs. Skipping two thirds of them is the right trade on the router, where the Dijkstra is the scarce work and the bookkeeping is not.

`YourRouter`는 이벤트 사이에 도달 가능한 라우터마다 거리와 부모, 그리고 포워딩 표를 들고 있다. 라우터당 숫자 하나와 이름 하나이고, 여기서는 400개다.

그 트리에 없는 링크는 끊기거나 나빠져도 SPF가 필요 없다. 더 짧아진 링크, 더 먼저 pop될 같은 비용, 그리고 다른 링크가 새 거리를 맞출 수 있는 상황에서 트리 링크가 끊기거나 나빠지는 경우는 여전히 SPF 전체를 돈다. 그게 329번이고, 1001번보다 67% 적다. 틀린 표는 없다. 판정은 good이고, 75% 선에는 못 미친다.

벽시계 시간은 반대다. 기준선 1.96초에 대해 3.23초다. 더 든 시간은 파이썬이 부모 목록을 걷는 시간이다. 라우터에게 모자란 것은, 플랩 한 번에 모든 라우터가 다시 계산할 때의 컨트롤 플레인 CPU이고, 그게 1001번이다. 그중 3분의 2를 건너뛰는 것이 라우터에서는 맞는 교환이다. Dijkstra가 비싼 일이고, 그 부기 작업은 그렇지 않다.
