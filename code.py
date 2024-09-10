import _ncs
import ncs.maapi as maapi
import ncs.maagic as maagic
import ncs


def delete_zombie(service_path, cleanup_logs):
    with maapi.single_write_trans("", "system", db=_ncs.OPERATIONAL) as wth:
        zombie_kp = "/ncs:zombies/ncs:service{{{}}}".format(service_path)
        if wth.exists(zombie_kp):
            cleanup_logs.append("Removing zombie service: {}".
                                format(zombie_kp))
            wth.delete(zombie_kp)
            wth.apply()


def remove_devices(devices, cleanup_logs):
    @ncs.maapi.retry_on_conflict()
    def remove_devices_with_retry(devices):
        with maapi.single_write_trans("", "system", db=_ncs.RUNNING) as wth:
            device_path = "/ncs:devices/device{{{}}}"

            for device_name in devices:
                if wth.exists(device_path.format(device_name)):
                    wth.delete(device_path.format(device_name))
                    cleanup_logs.append("Removed device {}".
                                        format(device_name))
            wth.apply()

    remove_devices_with_retry(devices)


def verify_plan_deletion(plan_path):
    with maapi.single_read_trans("", "system", db=_ncs.OPERATIONAL) as rth:
        return not rth.exists(plan_path)


def invoke_back_track_action(components, no_networking, cleanup_logs):
    for component in components:
        fbt_action = component.force_back_track
        fbt_input = fbt_action.get_input()
        if no_networking:
            fbt_input.no_networking.create()

        try:
            output = fbt_action(fbt_input)
        except Exception as ex:
            res_message = "Failed to force back track plan component {}: {}"\
                .format(component.name, ex)
        else:
            if not output.result:
                res_message = "Failed to force back track plan component"\
                    " {}: {}".format(component.name, output.info)
            else:
                res_message = "Force back track component {}.\n"\
                    "result: {} info {}".format(component.name,
                                                output.result, output.info)

        cleanup_logs.append(res_message)


def plan_cleanup(plan_path, no_networking, cleanup_logs):
    with maapi.single_read_trans("", "system", db=_ncs.OPERATIONAL) as rth:
        fbt_components = []

        if rth.exists(plan_path):
            plan_components = maagic.get_node(rth,
                                              plan_path + "/component")
            for component in plan_components:
                fbt_components.append(component)

        fbt_components.reverse()
        invoke_back_track_action(fbt_components,
                                 no_networking, cleanup_logs)


def get_kicker_with_service(service_path):
    kickers = []
    with maapi.single_read_trans("", "system", db=_ncs.RUNNING) as rth:
        qh = _ncs.maapi.query_start(rth.maapi.msock, rth.th,
                                    "/kickers/data-kicker/variable[value=\"" +
                                    service_path + "\"]", '/', 0, 1,
                                    _ncs.QUERY_STRING, ["../id"], [])

        res = _ncs.maapi.query_result(rth.maapi.msock, qh)

        for r in res:
            kickers.append(r[0])

        _ncs.maapi.query_stop(rth.maapi.msock, qh)
    return kickers


def remove_kickers(kickers, cleanup_logs):
    @ncs.maapi.retry_on_conflict()
    def remove_kickers_with_retry(kickers):
        with maapi.single_write_trans("", "system", db=_ncs.RUNNING) as wth:
            for kicker_id in kickers:
                kp = "/kickers/data-kicker{\"" + kicker_id + "\"}"
                if wth.exists(kp):
                    cleanup_logs.append("Removing kicker: %s" % kp)
                    wth.delete(kp)
            wth.apply()

    remove_kickers_with_retry(kickers)


def get_all_side_effect_for_service(service_path):
    side_effects = []
    with maapi.single_read_trans("", "system", db=_ncs.OPERATIONAL) as rth:
        qh = _ncs.maapi.query_start(rth.maapi.msock, rth.th,
                                    "/ncs:side-effect-queue/side-effect"
                                    + "[service=\"" + service_path + "\"]",
                                    '/', 0, 1, _ncs.QUERY_STRING, ["id"], [])

        res = _ncs.maapi.query_result(rth.maapi.msock, qh)

        for r in res:
            side_effects.append(r[0])

        _ncs.maapi.query_stop(rth.maapi.msock, qh)
    return side_effects


def remove_service_side_effects(side_effects, cleanup_logs):
    with maapi.single_write_trans("", "system", db=_ncs.OPERATIONAL) as wth:
        for side_effect_path in side_effects:
            kp = "/ncs:side-effect-queue/side-effect{{{}}}"\
                 .format(side_effect_path)
            if wth.exists(kp):
                cleanup_logs.append("Removing side-effect queue: %s" % kp)
                wth.delete(kp)
        wth.apply()

