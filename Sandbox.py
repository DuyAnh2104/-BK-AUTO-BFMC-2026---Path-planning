import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

GRAPH_FILE = "Competition_track_graph.graphml"
IMG_FILE = "Competition_track_graph.png"


current_extent = [-2.0, 22.0, -2.0, 16.0] 

MOVE_STEP = 0.5   # Di chuyển nhanh hay chậm
SCALE_STEP = 0.5  # Phóng to/thu nhỏ nhanh hay chậm

def on_key(event):
    global current_extent
   
    L, R, B, T = current_extent
    
    sys_msg = ""

    # --- NHÓM PHÍM DI CHUYỂN (MŨI TÊN) ---
    if event.key == 'right':
        L += MOVE_STEP; R += MOVE_STEP
        sys_msg = "Dịch Phải"
    elif event.key == 'left':
        L -= MOVE_STEP; R -= MOVE_STEP
        sys_msg = "Dịch Trái"
    elif event.key == 'up':
        B += MOVE_STEP; T += MOVE_STEP
        sys_msg = "Dịch Lên"
    elif event.key == 'down':
        B -= MOVE_STEP; T -= MOVE_STEP
        sys_msg = "Dịch Xuống"


    # Z: Thu nhỏ ảnh
    elif event.key == 'z':
        L += SCALE_STEP; R -= SCALE_STEP
        B += SCALE_STEP; T -= SCALE_STEP
        sys_msg = "Co nhỏ ảnh"
    # X: Phóng to ảnh 
    elif event.key == 'x':
        L -= SCALE_STEP; R += SCALE_STEP
        B -= SCALE_STEP; T += SCALE_STEP
        sys_msg = "Phóng to ảnh"
    
  
    # W: kéo dãn chiều cao
    elif event.key == 'w':
        T += SCALE_STEP
        sys_msg = "Tăng chiều cao"
    # S: thu hẹp chiều cao
    elif event.key == 's':
        T -= SCALE_STEP
        sys_msg = "Giảm chiều cao"
    # D: kéo dãn chiều rộng
    elif event.key == 'd':
        R += SCALE_STEP
        sys_msg = "Tăng chiều rộng"
    # A: thu hẹp chiều rộng
    elif event.key == 'a':
        R -= SCALE_STEP
        sys_msg = "Giảm chiều rộng"

    # Cập nhật và vẽ lại
    current_extent = [L, R, B, T]
    img_layer.set_extent(current_extent)
    fig.canvas.draw()
    
    
    print(f"[{sys_msg}] Extent MỚI: {current_extent}")
    print("-" * 30)


if not os.path.exists(GRAPH_FILE):
    print("Lỗi: Không tìm thấy file GraphML!")
    exit()

G = nx.read_graphml(GRAPH_FILE)
pos = {}
for n, data in G.nodes(data=True):
    x = float(data.get('x', data.get('d0', 0)))
    y = float(data.get('y', data.get('d1', 0)))
    pos[n] = (x, y)

fig, ax = plt.subplots(figsize=(14, 10))


nx.draw_networkx_nodes(G, pos, ax=ax, node_size=10, node_color='red')
nx.draw_networkx_edges(G, pos, ax=ax, edge_color='cyan', alpha=0.5)


if os.path.exists(IMG_FILE):
    img = mpimg.imread(IMG_FILE)
    img_layer = ax.imshow(img, extent=current_extent, aspect='auto', alpha=0.7) 
else:
    print("ko thấy ảnh nền")

ax.set_title("Dùng phím Mũi Tên (Dịch), Z/X (Zoom), W/A/S/D (Kéo dãn) để chỉnh. Nhìn Terminal lấy số!")
cid = fig.canvas.mpl_connect('key_press_event', on_key)

plt.show()