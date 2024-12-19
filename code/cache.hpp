#pragma once

#include <algorithm>
#include <cstdint>
#include <fstream>
#include <map>
#include <memory>
#include <optional>
#include <sstream>
#include <vector>

#include <gcache/ghost_kv_cache.h>
#include <gcache/stat.h>
#include <nlohmann/json.hpp>

#include "trace.hpp"

namespace mtcache {

using MissRateCurve = std::vector<std::tuple<
    /*count*/ uint32_t, /*size*/ uint32_t, /*miss_rate*/ gcache::CacheStat>>;
template <class Cache> class TenantCache {
  private:
    std::unique_ptr<Cache> cache;
    uint32_t reqs_processed;
    std::optional<uint64_t> first_ts;
    std::optional<uint64_t> last_ts;
    std::map<uint64_t, MissRateCurve> timed_miss_rate_curves;
    bool is_finalized;

    std::vector<std::string>
    miss_rate_curve_as_strings(const MissRateCurve& curve) const {
        std::vector<std::string> curve_strs;
        for (auto& point : curve) {
            std::ostringstream oss;
            oss << std::get<0>(point) << " " << std::get<1>(point)
                << std::get<2>(point);
            curve_strs.emplace_back(oss.view());
        }
        return curve_strs;
    }

  public:
    TenantCache<Cache>(uint32_t tick, uint32_t min_count, uint32_t max_count)
        : cache(std::make_unique<Cache>(tick, min_count, max_count)),
          is_finalized(false) {}

    void access(const TraceReq& req) {
        cache->access(req.key, req.keySize + req.valSize);
        if (last_ts) {
            last_ts = std::max(req.timeStamp, *last_ts);
        } else {
            first_ts = req.timeStamp;
            last_ts = req.timeStamp;
        }
        reqs_processed++;
    }

    void checkpoint_stats(uint64_t timestamp) {
        timed_miss_rate_curves.insert({timestamp, get_cache_stat_curve()});
    }

    void finalize() {
        assert(first_ts);
        assert(last_ts);
        is_finalized = true;
    }

    void dump_stats(const std::string& client, std::ofstream& outfile) const {
        using json = nlohmann::json;
        assert(is_finalized);

        json out_obj;
        out_obj["first_ts"] = *first_ts;
        out_obj["last_ts"] = *last_ts;
        out_obj["mrcs"] = json::object();
        for (auto kv : timed_miss_rate_curves) {
            out_obj["mrcs"][std::to_string(kv.first)] =
                miss_rate_curve_as_strings(kv.second);
        }
        outfile << out_obj.dump() << std::endl;
    }

    MissRateCurve get_cache_stat_curve() const {
        return cache->get_cache_stat_curve();
    }
};

} // namespace mtcache