#include <cstddef>
#include <cstdint>
#include <cstring>
#include <csv.hpp>
#include <filesystem>
#include <format>
#include <fstream>
#include <gcache/ghost_kv_cache.h>
#include <iostream>
#include <memory>
#include <string>
#include <utility>

#include "trace.hpp"

using mtcache::TraceReq;
using GhostKvCache = gcache::SampledGhostKvCache<1>;
using ClientsGhostMap =
    std::unordered_map<uint64_t, std::unique_ptr<GhostKvCache>>;
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

void initializeNewClientInGhost(uint64_t client,
                                ClientsGhostMap& clientsGhostMap) {
    clientsGhostMap[client] =
        std::make_unique<GhostKvCache>(64, 64, 1024);
    assert(clientsGhostMap[client] != nullptr);
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
    csv::CSVReader reader(file);

    ClientsGhostMap clientsGhostMap;

    int row_number = 1;
    for (csv::CSVRow& row : reader) {
        try {
            auto req = parser(row);
            req.printTraceReq();

            if (clientsGhostMap.find(req.client) == clientsGhostMap.end()) {
                initializeNewClientInGhost(req.client, clientsGhostMap);
            }

            assert(clientsGhostMap[req.client] != nullptr);
            clientsGhostMap[req.client]->access(req.key,
                                                req.keySize + req.valSize);
        } catch (const std::runtime_error& e) {
            std::cerr << "Skipped line " << row_number << " in trace ("
                      << e.what() << ")" << std::endl;
        }

        row_number++;
    }

    file.close();

    std::cout << "processed " << row_number << " requests";

    const std::string outdirpath("mrc");
    auto dirstat = fs::status(outdirpath);
    if (dirstat.type() == fs::file_type::not_found) {
        fs::create_directory(outdirpath);
    } else if (dirstat.type() != fs::file_type::directory) {
        std::cerr << "output directory \"" << outdirpath
                  << "\" exists but is not a directory";
        exit(1);
    }

    for (auto& kv : clientsGhostMap) {
        auto curve = kv.second->get_cache_stat_curve();
        if (curve.empty()) {
            // std::cout << "client \"" << kv.first << "\" is empty" <<
            // std::endl;
            continue;
        }
        std::ofstream outfile(fs::path(outdirpath) /
                              fs::path(std::to_string(kv.first)));
        saveMRCToFile(curve, outfile);
    }

    return 0;
}