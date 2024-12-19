#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <ostream>
#include <string>
#include <utility>

#include <csv.hpp>
#include <gcache/ghost_kv_cache.h>

#include "cache.hpp"
#include "trace.hpp"

// Time interval for MRC sampling
#define TIME_DELTA 60
// Cache configuration
#define MIN_CACHE (64)
#define MAX_CACHE (1024)
#define CACHE_STEP 64
#define SAMPLE 5

using mtcache::TraceReq, mtcache::TenantCache;
using GhostKvCache = gcache::SampledGhostKvCache<5>;
using ClientsGhostMap = std::unordered_map<uint64_t, TenantCache<GhostKvCache>>;
namespace fs = std::filesystem;

void saveMRCToFile(
    std::vector<std::tuple<uint32_t, uint32_t, gcache::CacheStat>> curve,
    std::ofstream& outstream) {
    for (auto& point : curve) {
        outstream << std::get<2>(point).get_hit_rate() << std::get<0>(point)
                  << " " << std::get<1>(point) << std::get<2>(point)
                  << std::endl;
    }
}

void usage(std::string& execname) {
    std::cout << "usage: " << execname << " <tw|fb> <trace>" << std::endl;
    exit(1);
}

int main(int argc, char* argv[]) {
    std::string execname(argv[0]);
    if (argc != 3) {
        usage(execname);
    }

    // Choose parser to use for trace
    std::string which_trace(argv[1]);
    std::function<TraceReq(csv::CSVRow&)> parser;
    if (which_trace == "tw") {
        parser = TraceReq::fromTwitterLine;
    } else if (which_trace == "fb") {
        parser = TraceReq::fromFacebookLine;
    } else {
        usage(execname);
    }

    // Open trace and setup CSV parser
    std::string trace_path(argv[2]);
    std::ifstream file(trace_path);
    if (!file.is_open()) {
        std::cerr << trace_path
                  << ": could not open file: " << std::strerror(errno)
                  << std::endl;
        exit(1);
    }

    ClientsGhostMap clientsGhostMap;
    uint64_t saveTs = 0;
    uint64_t row_number = 1;
    csv::CSVReader reader(file);

    for (csv::CSVRow& row : reader) {
        try {
            auto req = parser(row);
            if (!(row_number % 1000000)) {
                std::cout << "Processed " << row_number << " requests"
                          << std::endl;
            }

            // Save the MRC curves for each client with a certain time interval
            if (req.timeStamp - saveTs > TIME_DELTA) {
                saveTs = (req.timeStamp / TIME_DELTA) * TIME_DELTA;
                std::cout << "TS " << saveTs << std::endl;
                for (auto& kv : clientsGhostMap) {
                    kv.second.checkpoint_stats(saveTs);
                }
            }

            // printTraceReq(req);

            auto tenant_cache =
                clientsGhostMap.try_emplace(req.client, CACHE_STEP, MIN_CACHE, MAX_CACHE);
            tenant_cache.first->second.access(req);
        } catch (const std::runtime_error& e) {
            std::cerr << "Skipped line " << row_number << " in trace ("
                      << e.what() << ")" << std::endl;
        }
        row_number++;
    }

    auto outdir = fs::path("mrc");
    fs::create_directory(outdir);
    for (auto& kv : clientsGhostMap) {
        kv.second.finalize();

        auto client = std::to_string(kv.first);
        auto outpath = outdir / client;
        std::ofstream outstream(outpath);
        kv.second.dump_stats(outstream);
    }

    file.close();

    return 0;
}
