
require("scripts/autotracking/item_mapping")
require("scripts/autotracking/location_mapping")
require("scripts/autotracking/map_mapping")

Tracker:FindObjectForCode("blueemerald(#1)"):SetOverlay("Blue")
Tracker:FindObjectForCode("yellowemerald(#2)"):SetOverlay("Yellow")
Tracker:FindObjectForCode("pinkemerald(#3)"):SetOverlay("Pink")
Tracker:FindObjectForCode("greenemerald(#4)"):SetOverlay("Green")
Tracker:FindObjectForCode("redemerald(#5)"):SetOverlay("Red")
Tracker:FindObjectForCode("greyemerald(#6)"):SetOverlay("Grey")
Tracker:FindObjectForCode("disablegoalblocks"):SetOverlay("Buff")
Tracker:FindObjectForCode("disablerblocks"):SetOverlay("Buff")
Tracker:FindObjectForCode("greenhillkey"):SetOverlay("GHZ")
Tracker:FindObjectForCode("marblezonekey"):SetOverlay("MZ")
Tracker:FindObjectForCode("springyardkey"):SetOverlay("SYZ")
Tracker:FindObjectForCode("labyrinthkey"):SetOverlay("LZ")
Tracker:FindObjectForCode("starlightkey"):SetOverlay("SLZ")
Tracker:FindObjectForCode("scrapbrainkey"):SetOverlay("SBZ")
Tracker:FindObjectForCode("finalzonekey"):SetOverlay("FZ")
Tracker:FindObjectForCode("specialstage1key"):SetOverlay("Sp1")
Tracker:FindObjectForCode("specialstage2key"):SetOverlay("Sp2")
Tracker:FindObjectForCode("specialstage3key"):SetOverlay("Sp3")
Tracker:FindObjectForCode("specialstage4key"):SetOverlay("Sp4")
Tracker:FindObjectForCode("specialstage5key"):SetOverlay("Sp5")
Tracker:FindObjectForCode("specialstage6key"):SetOverlay("Sp6")

CUR_INDEX = -1
--SLOT_DATA = nil

SLOT_DATA = {}
AREA_KEY = ""

function has_value (t, val)
    for i, v in ipairs(t) do
        if v == val then return 1 end
    end
    return 0
end

function dump_table(o, depth)
    if depth == nil then
        depth = 0
    end
    if type(o) == 'table' then
        local tabs = ('\t'):rep(depth)
        local tabs2 = ('\t'):rep(depth + 1)
        local s = '{'
        for k, v in pairs(o) do
            if type(k) ~= 'number' then
                k = '"' .. k .. '"'
            end
            s = s .. tabs2 .. '[' .. k .. '] = ' .. dump_table(v, depth + 1) .. ','
        end
        return s .. tabs .. '}'
    else
        return tostring(o)
    end
end

function forceUpdate()
--    local update = Tracker:FindObjectForCode("update")
--    update.Active = not update.Active
end

function onClearHandler(slot_data)
    local clear_timer = os.clock()
    
    ScriptHost:RemoveWatchForCode("StateChange")
    -- Disable tracker updates.
    Tracker.BulkUpdate = true
    -- Use a protected call so that tracker updates always get enabled again, even if an error occurred.
    local ok, err = pcall(onClear, slot_data)
    -- Enable tracker updates again.
    if ok then
        -- Defer re-enabling tracker updates until the next frame, which doesn't happen until all received items/cleared
        -- locations from AP have been processed.
        local handlerName = "AP onClearHandler"
        local function frameCallback()
            ScriptHost:AddWatchForCode("StateChange", "*", StateChange)
            ScriptHost:RemoveOnFrameHandler(handlerName)
            Tracker.BulkUpdate = false
            forceUpdate()
            print(string.format("Time taken total: %.2f", os.clock() - clear_timer))
        end
        ScriptHost:AddOnFrameHandler(handlerName, frameCallback)
    else
        Tracker.BulkUpdate = false
        print("Error: onClear failed:")
        print(err)
    end
end

function onClear(slot_data)
    --SLOT_DATA = slot_data
    CUR_INDEX = -1
    -- reset locations
    for _, location_array in pairs(LOCATION_MAPPING) do
        for _, location in pairs(location_array) do
            if location then
                local lookingat = string.format("@%s/%s",location, location)
                local location_obj = Tracker:FindObjectForCode(lookingat)
                if location_obj then
                    location_obj.AvailableChestCount = 1
                end
            end
        end
    end
    -- reset items
    for _, item_tuple in pairs(ITEM_MAPPING) do
        local item_obj = Tracker:FindObjectForCode(item_tuple[1])
        if item_obj then
          if item_obj.Type == "toggle" then
              item_obj.Active = false
          end
        end
    end
    PLAYER_ID = Archipelago.PlayerNumber or -1
    TEAM_NUMBER = Archipelago.TeamNumber or 0
    SLOT_DATA = slot_data
    -- if Tracker:FindObjectForCode("autofill_settings").Active == true then
    --     autoFill(slot_data)
    -- end
    -- print(PLAYER_ID, TEAM_NUMBER)
    if Archipelago.PlayerNumber > -1 then

        HINTS_ID = "_read_hints_"..TEAM_NUMBER.."_"..PLAYER_ID
        Archipelago:SetNotify({HINTS_ID})
        Archipelago:Get({HINTS_ID})
        AREA_KEY = string.format("%s_%s_sonic1_area", PLAYER_ID, TEAM_NUMBER)
        Archipelago:SetNotify({AREA_KEY})
        Archipelago:Get({AREA_KEY})
    end
end

function onItem(index, item_id, item_name, player_number)
    if index <= CUR_INDEX then
        return
    end
    local is_local = player_number == Archipelago.PlayerNumber
    CUR_INDEX = index;
    local item = ITEM_MAPPING[item_id]
    print(string.format("handling %s - %s", item_id, item_name))
    if not item or not item[1] then
        --print(string.format("onItem: could not find item mapping for id %s", item_id))
        return
    end
    local item_obj = Tracker:FindObjectForCode(item[1])
    if item_obj then
      if item_obj.Type == "toggle" then
        -- print("toggle")
        item_obj.Active = true
      end
    else
        print(string.format("onItem: could not find object for code %s", item_code[1]))
    end
end

--called when a location gets cleared
function onLocation(location_id, location_name)
    local location_array = LOCATION_MAPPING[location_id]
    if not location_array or not location_array[1] then
        print(string.format("onLocation: could not find location mapping for id %s", location_id))
        return
    end
    
    for _, location in pairs(location_array) do
        print(string.format("handling %s - %s", location_id, location))
        local location_obj = Tracker:FindObjectForCode(string.format("@%s/%s",location, location))
        -- print(location, location_obj)
        if location_obj then
            location_obj.AvailableChestCount = 0
        else
            print(string.format("onLocation: could not find location_object for code %s", location))
        end
    end
    --canFinish()
end

function onEvent(key, value, old_value)
    updateEvents(value)
end

function onEventsLaunch(key, value)
    updateEvents(value)
end

-- this Autofill function is meant as an example on how to do the reading from slotdata and mapping the values to 
-- your own settings
-- function autoFill()
--     if SLOT_DATA == nil  then
--         print("its fucked")
--         return
--     end
--     -- print(dump_table(SLOT_DATA))

--     mapToggle={[0]=0,[1]=1,[2]=1,[3]=1,[4]=1}
--     mapToggleReverse={[0]=1,[1]=0,[2]=0,[3]=0,[4]=0}
--     mapTripleReverse={[0]=2,[1]=1,[2]=0}

--     slotCodes = {
--         map_name = {code="", mapping=mapToggle...}
--     }
--     -- print(dump_table(SLOT_DATA))
--     -- print(Tracker:FindObjectForCode("autofill_settings").Active)
--     if Tracker:FindObjectForCode("autofill_settings").Active == true then
--         for settings_name , settings_value in pairs(SLOT_DATA) do
--             -- print(k, v)
--             if slotCodes[settings_name] then
--                 item = Tracker:FindObjectForCode(slotCodes[settings_name].code)
--                 if item.Type == "toggle" then
--                     item.Active = slotCodes[settings_name].mapping[settings_value]
--                 else 
--                     -- print(k,v,Tracker:FindObjectForCode(slotCodes[k].code).CurrentStage, slotCodes[k].mapping[v])
--                     item.CurrentStage = slotCodes[settings_name].mapping[settings_value]
--                 end
--             end
--         end
--     end
-- end

function onNotify(key, value, old_value)
    print("onNotify", key, value, old_value)
    if value ~= old_value and key == HINTS_ID then
        for _, hint in ipairs(value) do
            if hint.finding_player == Archipelago.PlayerNumber then
                if hint.found then
                    updateHints(hint.location, true)
                else
                    updateHints(hint.location, false)
                end
            end
        end
    end
    if key == AREA_KEY then
      Tracker:UiHint("ActivateTab", AREA_MAPPING[value][1])
      if AREA_MAPPING[value][2] then
          Tracker:UiHint("ActivateTab", AREA_MAPPING[value][2])
      end
    end
end

function onNotifyLaunch(key, value)
    print("onNotifyLaunch", key, value)
    if key == HINTS_ID then
        for _, hint in ipairs(value) do
            print("hint", hint, hint.fount)
            print(dump_table(hint))
            if hint.finding_player == Archipelago.PlayerNumber then
                if hint.found then
                    updateHints(hint.location, true)
                else
                    updateHints(hint.location, false)
                end
            end
        end
    end
    if key == AREA_KEY then
      Tracker:UiHint("ActivateTab", AREA_MAPPING[value][1])
      if AREA_MAPPING[value][2] then
          Tracker:UiHint("ActivateTab", AREA_MAPPING[value][2])
      end
    end
end

function updateHints(locationID, clear)
    local item_codes = HINTS_MAPPING[locationID]

    for _, item_table in ipairs(item_codes, clear) do
        for _, item_code in ipairs(item_table) do
            local obj = Tracker:FindObjectForCode(item_code)
            if obj then
                if not clear then
                    obj.Active = true
                else
                    obj.Active = false
                end
            else
                print(string.format("No object found for code: %s", item_code))
            end
        end
    end
end


-- ScriptHost:AddWatchForCode("settings autofill handler", "autofill_settings", autoFill)
Archipelago:AddClearHandler("clear handler", onClearHandler)
Archipelago:AddItemHandler("item handler", onItem)
Archipelago:AddLocationHandler("location handler", onLocation)

Archipelago:AddSetReplyHandler("notify handler", onNotify)
Archipelago:AddRetrievedHandler("notify launch handler", onNotifyLaunch)



--doc
--hint layout
-- {
--     ["receiving_player"] = 1,
--     ["class"] = Hint,
--     ["finding_player"] = 1,
--     ["location"] = 67361,
--     ["found"] = false,
--     ["item_flags"] = 2,
--     ["entrance"] = ,
--     ["item"] = 66062,
-- } 
