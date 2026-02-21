"""
EAS 510 - Digital Forensics Detective
"""
import os
from rules import rule1_metadata, rule2_histogram, rule3_template
def scale_points(raw_score, raw_max, weight):
    """Rescale a rule score from [0..raw_max] to [0..weight]."""
    return int(round((raw_score / raw_max) * weight)) if raw_max > 0 else 0

class SimpleDetective:
    """An expert system that matches modified images to originals."""

    def __init__(self):
        self.targets = {}  # filename -> signature

    def register_targets(self, folder):
        """Load original images and compute signatures."""
        print(f"Loading targets from: {folder}")

        for filename in os.listdir(folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(folder, filename)
                file_size = os.path.getsize(filepath)

                self.targets[filename] = {
                    'path': filepath,
                    'size': file_size
                }
                print(f"  Registered: {filename} ({file_size} bytes)")

        print(f"Total targets: {len(self.targets)}")

    def find_best_match(self, input_image_path):
        print(f"\nProcessing: {os.path.basename(input_image_path)}")
        results = []

        for target_name, target_info in self.targets.items():
            # Rule 1
            r1, f1, e1 = rule1_metadata(target_info, input_image_path)

            # Rule 2
            r2, f2, e2 = rule2_histogram(target_info, input_image_path)

            # Rule 3
            r3, f3, e3 = rule3_template(target_info, input_image_path)

            total = r1 + r2 + r3  # 30 + 30 + 40 = 100 max

            results.append({
                "target": target_name,
                "total": total,
                "r1": (r1, f1, e1),
                "r2": (r2, f2, e2),
                "r3": (r3, f3, e3),
            })

        results.sort(key=lambda x: x["total"], reverse=True)
        best = results[0]

        r1, f1, e1 = best["r1"]
        r2, f2, e2 = best["r2"]
        r3, f3, e3 = best["r3"]

        # Print format matching the assignment example
        print(f"Rule 1 (Metadata): {'FIRED' if f1 else 'NO MATCH'} - {e1} -> {r1}/30 points")
        print(f"Rule 2 (Histogram): {'FIRED' if f2 else 'NO MATCH'} - {e2} -> {r2}/30 points")
        print(f"Rule 3 (Template): {'FIRED' if f3 else 'NO MATCH'} - {e3} -> {r3}/40 points")

        final = best["total"]

        # Starter threshold (tune later)
        if final >= 55:
            print(f"Final Score: {final}/100 -> MATCH to {best['target']}")
            return {"best_match": best["target"], "confidence": final}
        else:
            print(f"Final Score: {final}/100 -> REJECTED")
            return {"best_match": None, "confidence": final}


if __name__ == "__main__":
    print("=" * 50)
    print("SimpleDetective - Prototype v0.1")
    print("=" * 50)

    detective = SimpleDetective()
    detective.register_targets("originals")

    print("\n" + "=" * 50)
    print("TESTING")
    print("=" * 50)

    test_images = [
        "modified_images/modified_00_bright_enhanced.jpg",
        "modified_images/modified_03_compressed.jpg",
    ]

    for img in test_images:
        if os.path.exists(img):
            detective.find_best_match(img)
        else:
            print(f"Missing file: {img}")

    print("\n" + "=" * 50)
    print("PROTOTYPE COMPLETE!")
    print("=" * 50)