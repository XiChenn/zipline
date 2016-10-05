#
# Copyright 2016 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pandas import Timestamp


class CalendarRollFinder(object):

    def __init__(self, trading_calendar, asset_finder):
        self.trading_calendar = trading_calendar
        self.asset_finder = asset_finder

    def get_contract_center(self, root_symbol, dt, offset):
        oc = self.asset_finder.get_ordered_contracts(root_symbol)
        primary_candidate = oc.contract_before_auto_close(dt.value)

        # Here is where a volume check would be.
        primary = primary_candidate
        return oc.contract_at_offset(primary, offset)

    def get_rolls(self, root_symbol, start, end, offset):
        sessions = self.trading_calendar.all_sessions
        oc = self.asset_finder.get_ordered_contracts(root_symbol)
        primary_at_end = self.get_contract_center(root_symbol, end, 0)
        for i, sid in enumerate(oc.contract_sids):
            if sid == primary_at_end:
                break
        i += offset
        first = oc.contract_sids[i]
        rolls = [(first, None)]
        i -= 1
        auto_close_date = Timestamp(oc.auto_close_dates[i - offset], tz='UTC')
        while auto_close_date > start:
            # FIXME
            rolls.insert(0, (oc.contract_sids[i],
                             sessions[sessions.searchsorted(
                                 auto_close_date, side='left')]))
            auto_close_date = Timestamp(oc.auto_close_dates[i - offset],
                                        tz='UTC')
            i -= 1

        return rolls