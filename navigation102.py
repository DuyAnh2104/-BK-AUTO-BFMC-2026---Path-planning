import networkx as nx
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# --- PHẦN 1: CÁC HÀM TÍNH TOÁN ---

def calculate_distance(p1, p2):
    return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)

def get_angle(p1, p2, p3):
    v1 = np.array([p2['x'] - p1['x'], p2['y'] - p1['y']])
    v2 = np.array([p3['x'] - p2['x'], p3['y'] - p2['y']])
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if n1 == 0 or n2 == 0: return 0
    dot = np.dot(v1/n1, v2/n2)
    return np.degrees(np.arccos(np.clip(dot, -1.0, 1.0)))

# --- PHẦN 2: XỬ LÝ ĐỒ THỊ ---

def run_optimization(graph_file, img_file, start_node, end_node):
    # Đọc GraphML
    G = nx.read_graphml(graph_file)
    
    # Ép kiểu dữ liệu tọa độ
    for n in G.nodes():
        # NetworkX thường tự chuyển 'd0' thành 'x' dựa trên attr.name trong file của bạn
        # Chúng ta dùng .get() để tránh crash nếu node nào đó thiếu dữ liệu
        try:
            G.nodes[n]['x'] = float(G.nodes[n].get('x', G.nodes[n].get('d0', 0)))
            G.nodes[n]['y'] = float(G.nodes[n].get('y', G.nodes[n].get('d1', 0)))
        except KeyError:
            print(f"Cảnh báo: Node {n} không có dữ liệu tọa độ!")

    # Cấu hình vận tốc
    V_MAX = 1.0
    V_CURVE_MIN = 0.3

    for u, v in G.edges():
        dist = calculate_distance(G.nodes[u], G.nodes[v])
        velocity = V_MAX
        
        # Tính toán cua gắt dựa trên node tiếp theo (nếu có)
        successors = list(G.successors(v))
        if successors:
            angle = get_angle(G.nodes[u], G.nodes[v], G.nodes[successors[0]])
            if angle > 10:
                velocity = max(V_MAX * (1 - (angle/100)), V_CURVE_MIN)

        G[u][v]['weight'] = dist / velocity

    # Tìm đường bằng Dijkstra
    try:
        path = nx.dijkstra_path(G, source=start_node, target=end_node, weight='weight')
        print(f"Lộ trình tối ưu: {' -> '.join(path)}")
    except:
        print("Không tìm thấy đường!")
        return

    # --- PHẦN 3: HIỂN THỊ (VISUALIZATION) ---
    
    img = mpimg.imread(img_file)
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(img, extent=[0, 21, 0, 14]) # Scale extent dựa trên tọa độ trong XML (khoảng 0-21)

    # Vẽ toàn bộ đồ thị (mờ)
    pos = {n: (G.nodes[n]['x'], G.nodes[n]['y']) for n in G.nodes()}
    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.1, edge_color='gray', arrows=False)
    
    # Vẽ đường đi tối ưu (đậm)
    path_edges = list(zip(path, path[1:]))
    nx.draw_networkx_nodes(G, pos, nodelist=path, node_size=10, node_color='yellow', ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2, ax=ax, arrows=True)

    plt.title(f"Optimal Path: {start_node} to {end_node}")
    plt.legend(["Lộ trình tối ưu (Thời gian ngắn nhất)"])
    plt.show()

# --- CHẠY CHƯƠNG TRÌNH ---
# Thay đổi ID node bắt đầu và kết thúc tại đây
run_optimization("Competition_track_graph.graphml", "Competition_track_graph.png", "7", "333")