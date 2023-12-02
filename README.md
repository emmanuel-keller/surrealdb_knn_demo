Prerequisite:

```bash
pip install tensorflow keras-facenet
```

Launch Surreal

 ```bash
 cargo run -r start --allow-all -u ann -p ann -b 127.0.0.1:8000
 ```
 
Index the photos:

```bash
python knn_demo.py
```

Try face recognition:

```bash
python knn_demo.py samples/emmanuel2.jpg
```