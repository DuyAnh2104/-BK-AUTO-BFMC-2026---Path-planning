import networkx as nx
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time
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

# --- PHẦN 2: XỬ LÝ ĐỒ THỊ VÀ WAYPOINTS ---

def run_multi_point_optimization(graph_file, img_file, points_list):
    """
    points_list: Danh sách các Node ID muốn đi qua theo thứ tự.
    Ví dụ: ["7", "155", "333", "50"]
    """
    G = nx.read_graphml(graph_file)
    
    # Ép kiểu dữ liệu tọa độ
    for n in G.nodes():
        G.nodes[n]['x'] = float(G.nodes[n].get('x', G.nodes[n].get('d0', 0)))
        G.nodes[n]['y'] = float(G.nodes[n].get('y', G.nodes[n].get('d1', 0)))

    # Cấu hình vận tốc và trọng số (giống như cũ)
    V_MAX = 1.0
    V_CURVE_MIN = 0.3
    for u, v in G.edges():
        dist = calculate_distance(G.nodes[u], G.nodes[v])
        velocity = V_MAX
        successors = list(G.successors(v))
        if successors:
            angle = get_angle(G.nodes[u], G.nodes[v], G.nodes[successors[0]])
            if angle > 10:
                velocity = max(V_MAX * (1 - (angle/100)), V_CURVE_MIN)
        G[u][v]['weight'] = dist / velocity

    # TÌM ĐƯỜNG NỐI TIẾP NHAU
    full_path = []
    total_time = 0
    
    print(f"Bắt đầu tính toán lộ trình qua {len(points_list)} điểm...")
    
    for i in range(len(points_list) - 1):
        start = points_list[i]
        end = points_list[i+1]
        try:
            segment = nx.dijkstra_path(G, source=start, target=end, weight='weight')
            print(f"Lộ trình tối ưu: {' -> '.join(segment)} \n")
            segment_time = nx.dijkstra_path_length(G, source=start, target=end, weight='weight')
            
            # Tránh lặp lại điểm nối giữa các đoạn
            if i == 0:
                full_path.extend(segment)
            else:
                full_path.extend(segment[1:]) # Bỏ điểm đầu vì nó trùng với điểm cuối đoạn trước
            
            total_time += segment_time
            end_time = time.time()
        except nx.NetworkXNoPath:
            print(f"LỖI: Không thể tìm thấy đường từ {start} đến {end}!")
            return
    cal_time=end_time-time_start
    print(f"Lộ trình hoàn tất. tính toán hết {cal_time} Tổng thời gian dự kiến: {total_time:.2f} giây")

    # --- PHẦN 3: HIỂN THỊ ---
    img = mpimg.imread(img_file)
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Căn chỉnh lại extent để khớp với ảnh (thử thay đổi các số này nếu vẫn lệch)
    # extent=[x_min, x_max, y_min, y_max]
    myextent = [-1.0, 21.0, -1.0, 15.0]
    ax.imshow(img, extent=myextent) 

    pos = {n: (G.nodes[n]['x'], G.nodes[n]['y']) for n in G.nodes()}
    
    # Vẽ toàn bộ đồ thị ẩn phía dưới
    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.05, edge_color='white', arrows=False)
    
    # Vẽ lộ trình tối ưu qua nhiều điểm
    path_edges = list(zip(full_path, full_path[1:]))
    nx.draw_networkx_nodes(G, pos, nodelist=full_path, node_size=8, node_color='yellow', ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2, ax=ax, arrows=True)

    # Đánh dấu các điểm Waypoints chính
    waypoint_pos = {n: pos[n] for n in points_list}
    nx.draw_networkx_nodes(G, pos, nodelist=points_list, node_size=50, node_color='blue', label='Waypoints', ax=ax)

    plt.title(f"Multi-point Optimal Path: {' -> '.join(points_list)}")
    plt.legend()
    plt.show()

# --- CHẠY CHƯƠNG TRÌNH ---
# Định nghĩa danh sách các điểm bạn muốn đi qua tại đây
time_start= time.time()
my_waypoints = ["7", "333", "244", "33"] 
run_multi_point_optimization("Competition_track_graph.graphml", "Competition_track_graph.png", my_waypoints)