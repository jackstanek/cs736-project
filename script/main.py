import sys
import cache
import matplotlib.pyplot as plt

def parse_line(line):
    parts = line.strip().split(",")
    request = {
        "timestamp": int(parts[0]),
        "key": parts[1],
        "key_size": int(parts[2]),
        "value_size": int(parts[3]),
        "client": parts[4],
        "operation": parts[5]
    }
    return request


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <input file>")
        sys.exit(1)

    input_file = open(sys.argv[1])

    req_cache = cache.Cache(100000)

    cache_states = []
    last_ts = -1
    sample = 1

    for line in input_file:
        request = parse_line(line)
        if request["timestamp"] != last_ts and last_ts != -1 and request["timestamp"] % sample == 0:
            cache_states.append((last_ts, req_cache.get_state()))
        last_ts = request["timestamp"]
        # TODO other operations
        if request["operation"] == "add" or request["operation"] == "set":
            req_cache.add(request)

    X = []
    y_values = {}
    clients = [k for k,_ in cache_states[1][1].items()]
    for client in clients:
        y_values[client] = []
    for point in cache_states:
        X.append(point[0])
        for client in clients:
            val = 0
            if client in point[1]:
                val = point[1][client]
            y_values[client].append(val)

    for (k,Y) in y_values.items():
        plt.plot(X, Y)

    plt.show()

    print(cache_states)