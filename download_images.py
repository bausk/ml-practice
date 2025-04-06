import urllib.request
import os

# Ensure the directory exists
os.makedirs('labs-sources/images/ai-lab-2025-05', exist_ok=True)

# Define the image URLs and their target filenames
images = [
    ('https://i.ibb.co/Jr88sn2/mit.png', 'image01.png'),
    ('https://i.ibb.co/2P3SLwK/colab.png', 'image02.png'),
    ('https://i.ibb.co/xfJbPmL/github.png', 'image03.png'),
    ('https://raw.githubusercontent.com/MITDeepLearning/introtodeeplearning/2025/lab1/img/add-graph.png', 'image04.png'),
    ('https://raw.githubusercontent.com/MITDeepLearning/introtodeeplearning/2025/lab1/img/computation-graph.png', 'image05.png'),
    ('https://raw.githubusercontent.com/MITDeepLearning/introtodeeplearning/2025/lab1/img/computation-graph-2.png', 'image06.png'),
    # New images from the music generation notebook
    ('http://33.media.tumblr.com/3d223954ad0a77f4e98a7b87136aa395/tumblr_nlct5lFVbF1qhu7oio1_500.gif', 'image07.gif'),
    ('https://raw.githubusercontent.com/MITDeepLearning/introtodeeplearning/2019/lab1/img/lstm_unrolled-01-01.png', 'image08.png'),
    ('https://raw.githubusercontent.com/MITDeepLearning/introtodeeplearning/2019/lab1/img/lstm_inference.png', 'image09.png')
]

# Download each image
for url, filename in images:
    target_path = os.path.join('labs-sources/images/ai-lab-2025-05', filename)
    try:
        print(f"Downloading {url} to {target_path}")
        urllib.request.urlretrieve(url, target_path)
        print(f"Successfully downloaded {filename}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

# Try alternative year for the first three PyTorch images if they failed previously
alternative_images = [
    ('https://raw.githubusercontent.com/MITDeepLearning/introtodeeplearning/master/lab1/img/add-graph.png', 'image04.png'),
    ('https://raw.githubusercontent.com/MITDeepLearning/introtodeeplearning/master/lab1/img/computation-graph.png', 'image05.png'),
    ('https://raw.githubusercontent.com/MITDeepLearning/introtodeeplearning/master/lab1/img/computation-graph-2.png', 'image06.png'),
]

# Check which images might be missing and try alternative URLs
for url, filename in alternative_images:
    target_path = os.path.join('labs-sources/images/ai-lab-2025-05', filename)
    if not os.path.exists(target_path) or os.path.getsize(target_path) == 0:
        try:
            print(f"Trying alternative URL for {filename}")
            print(f"Downloading {url} to {target_path}")
            urllib.request.urlretrieve(url, target_path)
            print(f"Successfully downloaded {filename}")
        except Exception as e:
            print(f"Error downloading {url}: {e}") 