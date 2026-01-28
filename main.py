import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

def visualize_full_graph(graph_file, img_file):
    # 1. Tải đồ thị từ file GraphML
    if not os.path.exists(graph_file):
        print(f"Lỗi: Không tìm thấy file {graph_file}")
        return
    
    G = nx.read_graphml(graph_file)
    
    # 2. Trích xuất tọa độ và ép kiểu về float
    pos = {}
    for n, data in G.nodes(data=True):
        # Lấy tọa độ x, y từ key 'x', 'y' hoặc 'd0', 'd1' tùy phiên bản lưu
        x = float(data.get('x', data.get('d0', 0)))
        y = float(data.get('y', data.get('d1', 0)))
        pos[n] = (x, y)
        # Cập nhật lại vào node để dùng cho các tính toán khác nếu cần
        G.nodes[n]['x'] = x
        G.nodes[n]['y'] = y

    # 3. Thiết lập Figure và nạp ảnh nền
    fig, ax = plt.subplots(figsize=(15, 10))
    
    if os.path.exists(img_file):
        img = mpimg.imread(img_file)
        
        # THÔNG SỐ QUAN TRỌNG: Căn chỉnh extent để khớp ảnh
        # Bạn đã thử [-1.0, 21.0, -1.0, 15.0], hãy tinh chỉnh các số này ở đây
        my_extent = [-0.0706, 20.7606, 0.0574, 13.7126] 
        
        ax.imshow(img, extent=my_extent, aspect='auto')
        print(f"Đã nạp ảnh {img_file} với extent: {my_extent}")
    else:
        print(f"Cảnh báo: Không thấy ảnh {img_file}, vẽ trên nền trắng.")

    # 4. Vẽ toàn bộ đồ thị
    # Vẽ các cạnh (đường nối giữa các điểm)
    nx.draw_networkx_edges(
        G, pos, 
        ax=ax, 
        edge_color='cyan', 
        width=0.8, 
        alpha=0.6, 
        arrows=True, 
        arrowsize=7
    )
    
    # Vẽ các nút (điểm)
    nx.draw_networkx_nodes(
        G, pos, 
        ax=ax, 
        node_size=5, 
        node_color='red', 
        alpha=0.8
    )

    # (Tùy chọn) Hiện ID của node nếu muốn kiểm tra số hiệu điểm
    # nx.draw_networkx_labels(G, pos, font_size=6, font_color='white')

    ax.set_title("Ướm thử toàn bộ mạng lưới điểm lên đường đua")
    ax.axis('on') # Hiện thước đo để dễ căn chỉnh extent
    plt.tight_layout()
    plt.show()

# --- CHẠY CHƯƠNG TRÌNH ---
# Đảm bảo tên file đúng với file bạn đang có
graph_filename = "Competition_track_graph.graphml"
image_filename = "Competition_track_graph.png"

visualize_full_graph(graph_filename, image_filename)