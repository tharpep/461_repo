from schema import ProjectMetadata

project: ProjectMetadata = {
    "name": "Example Project",  
    "category": "MODEL",
    "net_score": 0.85,
    "net_score_latency": 2,
    "ramp_up_time": 1.5,
    "ramp_up_time_latency": 1,
    "bus_factor": 0.9,
    "bus_factor_latency": 1,
    "performance_claims": 0.95,
    "performance_claims_latency": 2,
    "license": 1.0,
    "license_latency": 1,
    "size_score": {"raspberry_pi": 0.8, "jetson_nano": 0.9},
    "size_score_latency": 2,
    "dataset_and_code_score": 0.9,
    "dataset_and_code_score_latency": 2,
    "dataset_quality": 0.85,
    "dataset_quality_latency": 2,
    "code_quality": 0.9,
    "code_quality_latency": 2,
}

def process_metadata(data: ProjectMetadata) -> None:
    print(data["name"])
    print(data["category"])

if __name__ == "__main__":
    process_metadata(project)