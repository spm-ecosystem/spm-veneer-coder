import concurrent.futures
import json
import time
import urllib.request


def test_veneer_worker(task_id):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "veneer-coder",
        "prompt": (
            f"Reconstruct task {task_id}: map #element-{task_id} to"
            f" UiComponent{task_id}"
        ),
        "stream": False,
        "options": {"temperature": 0.2},
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    start = time.time()

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            res = json.loads(response.read().decode("utf-8"))
            duration = time.time() - start

            return (
                task_id,
                True,
                duration,
                res.get("response", "").strip(),
            )

    except Exception as e:
        return task_id, False, time.time() - start, str(e)


def run_stress_test(num_requests=20, max_workers=5):
    print(
        f"[INFO] Starting stress test: "
        f"{num_requests} requests, "
        f"{max_workers} concurrent workers"
    )

    start_total = time.time()
    successes = 0

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:
        futures = [
            executor.submit(test_veneer_worker, i)
            for i in range(num_requests)
        ]

        for future in concurrent.futures.as_completed(futures):
            task_id, success, duration, result = future.result()

            if success:
                successes += 1
                output = result.replace("\n", " ")[:80]

                print(
                    f"[SUCCESS] Task {task_id:04d} | "
                    f"Duration: {duration:7.2f}s | "
                    f"Output: {output}..."
                )
            else:
                print(
                    f"[ERROR]   Task {task_id:04d} | "
                    f"Duration: {duration:7.2f}s | "
                    f"Error: {result}"
                )

    total_time = time.time() - start_total
    failures = num_requests - successes
    throughput = num_requests / total_time if total_time > 0 else 0

    print("\n" + "=" * 60)
    print("STRESS TEST SUMMARY")
    print("=" * 60)
    print(f"Total requests : {num_requests}")
    print(f"Successful     : {successes}")
    print(f"Failed         : {failures}")
    print(f"Total duration : {total_time:.2f}s")
    print(f"Throughput     : {throughput:.2f} req/s")
    print("=" * 60)


if __name__ == "__main__":
    run_stress_test(num_requests=100, max_workers=10)