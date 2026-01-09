import networkx as nx
import math
import numpy as np

def calculate_distance(p1, p2):
    """Tính khoảng cách Euclid giữa 2 điểm"""
    return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)

def get_angle(p1, p2, p3):
    """Tính góc giữa 2 vector nối 3 điểm liên tiếp (độ lệch hướng)"""
    v1 = np.array([p2['x'] - p1['x'], p2['y'] - p1['y']])
    v2 = np.array([p3['x'] - p2['x'], p3['y'] - p2['y']])
    
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 == 0 or norm2 == 0:
        return 0
    
    # Tính cosin của góc giữa 2 vector
    unit_v1 = v1 / norm1
    unit_v2 = v2 / norm2
    dot_product = np.dot(unit_v1, unit_v2)
    
    # Trả về góc (độ) - góc càng lớn xe càng phải cua gắt
    angle = np.arccos(np.clip(dot_product, -1.0, 1.0))
    return np.degrees(angle)

def process_track_graph(file_path, start_node, end_node):
    # 1. Đọc đồ thị
    G = nx.read_graphml(file_path)
    
    # Chuyển đổi dữ liệu tọa độ sang kiểu số (float)
    for node_id in G.nodes():
        x_val = G.nodes[node_id].get('x', G.nodes[node_id].get('d0', 0))
        y_val = G.nodes[node_id].get('y', G.nodes[node_id].get('d1', 0))
    
        G.nodes[node_id]['x'] = float(x_val)
        G.nodes[node_id]['y'] = float(y_val)

        

    # Tham số giả định (Tùy chỉnh theo thực tế robot của bạn)
    V_MAX = 1.0        # Vận tốc tối đa trên đường thẳng (m/s)
    V_CURVE_MIN = 0.3  # Vận tốc tối thiểu khi cua gắt (m/s)
    STOP_PENALTY = 2.0 # Phạt 2 giây tại vạch dừng/biển báo
    
    # 2. Tính toán Weight cho từng cạnh
    for u, v in G.edges():
        node_u = G.nodes[u]
        node_v = G.nodes[v]
        
        # Khoảng cách cơ bản
        dist = calculate_distance(node_u, node_v)
        
        # Mặc định vận tốc là tối đa
        velocity = V_MAX
        
        # --- LOGIC ĐỘ CONG ---
        # Kiểm tra các nút tiếp theo để biết đây có phải khúc cua không
        successors = list(G.successors(v))
        if successors:
            next_node = G.nodes[successors[0]]
            curve_angle = get_angle(node_u, node_v, next_node)
            
            # Nếu góc lệch > 10 độ, bắt đầu giảm tốc
            if curve_angle > 10:
                # Giảm tốc tỷ lệ thuận với độ gắt của góc
                reduction = np.clip(curve_angle / 90.0, 0, 0.7) 
                velocity = V_MAX * (1 - reduction)
                velocity = max(velocity, V_CURVE_MIN)

        # --- LOGIC LUẬT GIAO THÔNG ---
        traffic_penalty = 0
        
        # Ví dụ: Nếu node v nằm trong danh sách các điểm có vạch dừng (cần nạp ID thủ công)
        # stop_nodes = ["100", "250"] 
        # if v in stop_nodes: traffic_penalty += STOP_PENALTY
        
        # Ví dụ: Phạt thời gian nếu đi vào vùng Roundabout (vòng xuyến)
        # Giả sử tọa độ x trong khoảng [6, 7.5] và y trong [4, 5.5] là vòng xuyến
        if 6.5 < node_v['x'] < 7.5 and 4.0 < node_v['y'] < 5.5:
            velocity *= 0.5 # Giảm 50% tốc độ khi vào vòng xuyến
            traffic_penalty += 0.5 # Phạt thêm rủi ro va chạm

        # TÍNH TỔNG THỜI GIAN (WEIGHT)
        # t = s / v + penalty
        G[u][v]['weight'] = (dist / velocity) + traffic_penalty

    # 3. Tìm đường đi tối ưu bằng Dijkstra
    try:
        best_path = nx.dijkstra_path(G, source=start_node, target=end_node, weight='weight')
        total_time = nx.dijkstra_path_length(G, source=start_node, target=end_node, weight='weight')
        
        print(f"Đường đi từ {start_node} đến {end_node}:")
        print(" -> ".join(best_path))
        print(f"\nTổng thời gian dự kiến: {total_time:.2f} giây")
        
        return best_path, G
    except nx.NetworkXNoPath:
        print("Không tìm thấy đường đi tuân thủ luật!")
        return None, G

# Chạy thử nghiệm
file_name = "Competition_track_graph.graphml" # Đảm bảo file này nằm cùng thư mục
path, updated_G = process_track_graph(file_name, "1", "520")

# Lưu lại file GraphML mới có chứa weight để kiểm tra bằng Gephi hoặc phần mềm khác
nx.write_graphml(updated_G, "Processed_Track.graphml")