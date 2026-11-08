import asyncio
import time
import statistics
from pathlib import Path
from evaluation.performance.perf_client import PerformanceTesterClient

import json
import matplotlib.pyplot as plt

IMAGES_FOLDER = Path("../images")

class PerformanceTestSuite:
    def __init__(self):
        self.client = PerformanceTesterClient()


    def _print_report(self, scenario_name: str):
        print(f"\n[{scenario_name}] - RESULTS")
        latencies = []
        for task_id, data in self.client.tracking_data.items():
            if data["received_at"] is not None:
                latencies.append((data["received_at"] - data["sent_at"]) * 1000)

        total_sent = len(self.client.tracking_data)
        total_received = len(latencies)
        lost = total_sent - total_received

        print(f" -> Total sent: {total_sent}")
        print(f" -> Successfully processed: {total_received}")
        print(f" -> Lost in transit: {lost}")

        if latencies:
            print(f" -> MIN latency: {min(latencies):.2f} ms")
            print(f" -> MAX latency: {max(latencies):.2f} ms")
            print(f" -> AVERAGE latency: {statistics.mean(latencies):.2f} ms")
            if total_received > 1:
                print(f" -> Median: {statistics.median(latencies):.2f} ms")
            if total_received >= 10:
                print(f" -> p95 (95th percentile): {statistics.quantiles(latencies, n=100)[94]:.2f} ms")


    async def test_single_latency(self, count: int = 5):
        """Sends one image at a time and waits to measure the pure, uninterrupted E2E response time."""
        print(f"\n--- STARTING BASELINE E2E TEST ({count} images) ---")
        self.client.clear_tracker()

        for _ in range(count):
            await self.client.upload_image(IMAGES_FOLDER)
            await asyncio.sleep(2)

        await self.wait_for_queue_to_drain(idle_time=10)
        self._print_report("Baseline latency test")


    async def test_constant_belt_speed(self, interval_ms: int, duration_sec: int):
        """Simulates a conveyor belt by sending images at a constant rate for a specified time."""
        print(f"\n--- STARTING CONVEYOR BELT SPEED TEST (One image every {interval_ms}ms for {duration_sec}s) ---")
        self.client.clear_tracker()

        sleep_sec = interval_ms / 1000.0
        end_time = time.time() + duration_sec
        background_tasks = []

        while time.time() < end_time:
            loop_start = time.time()
            
            task = asyncio.create_task(self.client.upload_image(IMAGES_FOLDER))
            background_tasks.append(task)
            
            elapsed = time.time() - loop_start
            await asyncio.sleep(max(0, sleep_sec - elapsed))
        
        await asyncio.gather(*background_tasks)
        
        await self.wait_for_queue_to_drain(idle_time=10)
        self._print_report(f"Conveyor belt test ({interval_ms}ms)")


    async def test_burst(self, burst_size: int = 50):
        print(f"\n--- STARTING THROUGHPUT TEST (Burst: {burst_size} images in a fraction of a second) ---")
        self.client.clear_tracker()

        tasks = [self.client.upload_image(IMAGES_FOLDER) for _ in range(burst_size)]
        await asyncio.gather(*tasks)

        await self.wait_for_queue_to_drain(idle_time=10)
        
        self._print_report(f"API burst test ({burst_size} requests)")


    async def wait_for_queue_to_drain(self, idle_time: int = 5):
        print(f"\n[INFO] Waiting for the queue to drain (clearing remaining items)...")
        last_count = len([d for d in self.client.tracking_data.values() if d["received_at"] is not None])
        
        while True:
            await asyncio.sleep(idle_time)
            current_count = len([d for d in self.client.tracking_data.values() if d["received_at"] is not None])
            if current_count == last_count:
                print("[INFO] The queue appears to be empty. The next test can be started!\n")
                break
            last_count = current_count


    async def test_burst_for_graph(self, burst_size: int = 50):
        print(f"\n=== START: BURST TEST FOR GRAPH (Burst: {burst_size} images) ===")
        self.client.clear_tracker()

        burst_start_time = time.time()

        tasks = [self.client.upload_image(IMAGES_FOLDER) for _ in range(burst_size)]
        await asyncio.gather(*tasks)

        await self.wait_for_queue_to_drain(idle_time=5)

        completed_tasks = [t for t in self.client.tracking_data.values() if t["received_at"] is not None]
        completed_tasks.sort(key=lambda x: x["received_at"])
        completion_times_sec = [(t["received_at"] - burst_start_time) for t in completed_tasks]

        if not completion_times_sec:
            print("[ERROR] No task was received.")
            return

        total_recovery_time = completion_times_sec[-1]
        throughput_fps = len(completed_tasks) / total_recovery_time

        print("\n[BURST TEST RESULTS]")
        print(f" -> Number of processed tasks: {len(completed_tasks)} / {burst_size}")
        print(f" -> Total queue recovery time: {total_recovery_time:.2f} s")
        print(f" -> Actual hardware throughput under stress: {throughput_fps:.2f} FPS")

        plt.figure(figsize=(10, 6))
        x_axis = list(range(1, len(completed_tasks) + 1))

        plt.plot(x_axis, completion_times_sec, marker='o', markersize=5, linestyle='-', color='#e74c3c', label="Actual completion time")

        plt.title(f"API burst test ({burst_size} concurrent requests)", fontsize=14, pad=15)
        plt.xlabel("Processed request number", fontsize=12)
        plt.ylabel("Time since start [s]", fontsize=12)
        
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.legend(loc='upper left', fontsize=10)
        plt.tight_layout()

        img_name = f"wykres_burst_{burst_size}.png"
        plt.savefig(img_name, dpi=300)
        print(f"[SUCCESS] Graph generated in file: {img_name}")


    async def test_series_for_graph(self, count_per_series: int = 100, intervals_ms: list = [500, 400, 300, 250, 200, 150, 100, 75, 50]):
        print(f"\n=== START: EXTENDED GRAPH TEST ({count_per_series} images / series) ===")
        all_series_latencies = {}

        for interval_ms in intervals_ms:
            print(f"\n--- Starting series: {interval_ms} ms ---")
            self.client.clear_tracker()
            sleep_sec = interval_ms / 1000.0
            background_tasks = []

            for _ in range(count_per_series):
                loop_start = time.time()
                
                task = asyncio.create_task(self.client.upload_image(IMAGES_FOLDER))
                background_tasks.append(task)
                
                elapsed = time.time() - loop_start
                await asyncio.sleep(max(0, sleep_sec - elapsed))

            await asyncio.gather(*background_tasks)
            await self.wait_for_queue_to_drain(idle_time=10)

            sorted_tasks = sorted(self.client.tracking_data.values(), key=lambda t: t["sent_at"])
            
            current_latencies = []
            for t in sorted_tasks:
                if t["received_at"] is not None:
                    current_latencies.append(round((t["received_at"] - t["sent_at"]) * 1000, 2))
                else:
                    current_latencies.append(None)
            
            all_series_latencies[str(interval_ms)] = current_latencies
            self._print_report(f"Summary for series {interval_ms}ms")

        self._export_to_json_and_plot(all_series_latencies, count_per_series)

    def _export_to_json_and_plot(self, data: dict, count: int, filename_prefix: str = "test_results"):
        
        json_filename = f"{filename_prefix}.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"\n[SUCCESS] Measurement data saved to file: {json_filename}")

        plt.figure(figsize=(12, 8))
        x_axis = list(range(1, count + 1))
        
        for interval_str, latencies in data.items():
            y_axis = [lat if lat is not None else 0 for lat in latencies]
            
            plt.plot(x_axis, y_axis, marker='.', markersize=4, linewidth=1.5, label=f"{interval_str} ms")

        plt.title("Queue buildup phenomenon", fontsize=14, pad=15)
        plt.xlabel("Request number in series", fontsize=12)
        plt.ylabel("End-to-end latency [ms]", fontsize=12)
        
        
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.legend(title="Request interval", bbox_to_anchor=(1.01, 1), loc='upper left')
        plt.tight_layout()

        png_filename = f"{filename_prefix}.png"
        plt.savefig(png_filename, dpi=300)
        print(f"[SUCCESS] Graph generated in file: {png_filename}")


async def main():
    suite = PerformanceTestSuite()
    listener_task = asyncio.create_task(suite.client.start_listener())

    await suite.test_burst(burst_size=10)

    await suite.test_constant_belt_speed(interval_ms=50, duration_sec=10)

    await suite.test_single_latency(count=25)

    await suite.test_series_for_graph()

    await suite.test_burst_for_graph(burst_size=100)

    print("[INFO] Tests completed. Closing connections.")
    await suite.client.close_connections()

    suite.client.stop()

if __name__ == "__main__":
    asyncio.run(main())