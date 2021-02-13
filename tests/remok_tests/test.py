from unittest import mock
import pathlib
import remok
import pytest
import re
from pytest_mock import mocker

HERE = pathlib.Path(__file__).resolve().parent


def subkernel_checks(subkernel, complete, keylist):
    keylist2 = [ 'apt purge {}'.format(x) for x in keylist ]
    assert subkernel.is_complete() is complete
    assert subkernel.tocmd() == '\n'.join(keylist2)



def subkernel_component_value(subkernel, key):
    if key == 'headers':
        return subkernel.headers
    elif key == 'modules':
        return subkernel.modules
    elif key == 'modules-extra':
        return subkernel.modules_extra
    elif key == 'image':
        return subkernel.image
    else:
        return 'unexpected_value'



def test_subkernel():
    val = remok.KernelSub()
    val.headers = 'linux-headers-5.4.0-62-generic'
    subkernel_checks(val, False, ['linux-headers-5.4.0-62-generic'])
    val.modules_extra = 'linux-modules-extra-5.4.0-62-generic'
    subkernel_checks(val, False, ['linux-headers-5.4.0-62-generic', 'linux-modules-extra-5.4.0-62-generic'])
    val.modules = 'linux-modules-5.4.0-62-generic'
    subkernel_checks(val, False, ['linux-headers-5.4.0-62-generic', 'linux-modules-5.4.0-62-generic',
                                  'linux-modules-extra-5.4.0-62-generic']) 
    val.image = 'linux-image-5.4.0-62-generic'
    subkernel_checks(val, True, ['linux-headers-5.4.0-62-generic', 'linux-modules-5.4.0-62-generic',
                                 'linux-modules-extra-5.4.0-62-generic', 'linux-image-5.4.0-62-generic'])
    val.headers, val.modules, val.modules_extra, val.image = [None for x in range(4)]
    
    for key in ('headers', 'image', 'modules', 'modules-extra'):
        component = {'name': 'testing', 'component': key}
        val.add_component(component)
        assert subkernel_component_value(val, key) == 'testing'
        val.headers, val.modules, val.modules_extra, val.image = [None for x in range(4)]



def kernel_change_component(component, key):
    component['name'] = key 
    component['component'] = key 
    component['type'] = 'generic'



def heuristic_kernel_cmd(components_total):
    complete_list = ['headers-base', 'headers', 'modules', 'modules-extra', 'image']
    actual_list = complete_list[:components_total]
    if components_total == 3:
        actual_list[2] = 'modules-extra'
    cmd_list = [ 'apt purge {}'.format(x) for x in actual_list ]
    return '\n'.join(cmd_list)



def test_kernel():
    component = {'name': 'headers-base', 'component': 'headers',
                 'version': [1,2,3,4], 'version_string': '1.2.3-4',
                 'type': 'base' }
    kernel = remok.Kernel([1,2,3,4])
    assert kernel.is_complete() is False
    kernel.add_component(component)
    assert kernel.tocmd() == 'apt purge headers-base\n'
    components_total = 1
    for complete, key in [(False, 'headers'), (False, 'modules-extra'),
                          (False, 'modules'), (True, 'image')]:
        kernel_change_component(component, key)
        kernel.add_component(component)
        components_total += 1
        assert kernel.is_complete() is complete
        assert heuristic_kernel_cmd(components_total) == kernel.tocmd()



def test_kernel_sorting():
    tlist = [(1,2,3,4), (4,2,5,1), (2,1,1,1), (1,7,0,0), (1,0,9,9)]
    slist = [(1,0,9,9), (1,2,3,4), (1,7,0,0), (2,1,1,1), (4,2,5,1)]
    kernels = []
    for kernel_version in tlist:
        kernels.append(remok.Kernel(kernel_version))
    for index, kernel in enumerate(sorted(kernels)):
        assert slist[index] == kernel.version



def test_arch_isvalid():
    assert remok.arch_is_valid('all') is True
    assert remok.arch_is_valid('amd64') is True
    assert remok.arch_is_valid('i386') is True
    for val in ('i246', '<unassigned>', 'amd65'): 
        assert remok.arch_is_valid(val) is False



def to_kinfo(string):
    # 1) headers, image, modules, modules-extra
    # 2) VERSION (1)
    # 3) VERSION (2)
    # 4) VERSION (3)
    # 5) VERSION (4)
    # 6) '' or 'generic'
    regexp = r'linux-(headers|image|modules-extra|modules)-(\d+).(\d+).(\d+)-(\d+)(.*)'
    m = re.match(regexp, string)
    if m.group(6) == '-generic':
        kinfo_type = 'generic'
    elif m.group(6) == '':
        kinfo_type = 'base'
    else:
        kinfo_type = 'nothing'
    return { 'name': string, 'component': m.group(1),
             'version': [ int(m.group(x)) for x in range(2,6) ],
             'version_string': '{}.{}.{}-{}'.format(*[m.group(x)  for x in range(2,6)]),
             'type': kinfo_type }



def test_get_kernel_infos(tmp_path):
    with mock.patch(
        "subprocess.check_output", return_value=(HERE / "test01.txt").read_bytes()
    ):
        assert remok.get_kernel_infos() == [
               to_kinfo('linux-headers-5.0.0-62'),
               to_kinfo('linux-headers-5.0.0-62-generic'),
               to_kinfo('linux-headers-5.0.0-65'),
               to_kinfo('linux-headers-5.0.0-65-generic'),
               to_kinfo('linux-image-5.0.0-62-generic'),
               to_kinfo('linux-image-5.0.0-65-generic'),
               to_kinfo('linux-modules-5.0.0-62-generic'),
               to_kinfo('linux-modules-5.0.0-65-generic'),
               to_kinfo('linux-modules-extra-5.0.0-62-generic'),
               to_kinfo('linux-modules-extra-5.0.0-65-generic'),
               to_kinfo('linux-headers-5.4.0-62'),
               to_kinfo('linux-headers-5.4.0-62-generic'),
               to_kinfo('linux-headers-5.4.0-65'),
               to_kinfo('linux-headers-5.4.0-65-generic'),
               to_kinfo('linux-image-5.4.0-62-generic'),
               to_kinfo('linux-image-5.4.0-65-generic'),
               to_kinfo('linux-modules-5.4.0-62-generic'),
               to_kinfo('linux-modules-5.4.0-65-generic'),
               to_kinfo('linux-modules-extra-5.4.0-62-generic'),
               to_kinfo('linux-modules-extra-5.4.0-65-generic')]



def kernel_set(kernel):
    version='{}.{}.{}-{}'.format(*kernel.version)
    kernel.kbase.headers = 'linux-headers-{}'.format(version)
    kernel.kgeneric.headers = 'linux-headers-{}-generic'.format(version)
    kernel.kgeneric.modules = 'linux-modules-{}-generic'.format(version)
    kernel.kgeneric.modules_extra = 'linux-modules-extra-{}-generic'.format(version)
    kernel.kgeneric.image = 'linux-image-{}-generic'.format(version)



def test_kernel_saving():
    with mock.patch(
        "subprocess.check_output", return_value=(HERE / "test01.txt").read_bytes()
    ):
        # this test reuses part of remok.main() code
        kernel_infos=remok.get_kernel_infos()
        kernels = {}
        for kinfo in kernel_infos:
            version = kinfo['version_string']
            if version not in kernels:
                kernels[version] = remok.Kernel(kinfo['version'])
            kernels[version].add_component(kinfo)
        kernel_list=list(kernels.values())
        to_save, to_delete = remok.kernels_to_save_delete(kernel_list)
        expected_delete = [remok.Kernel([5,0,0,62]), remok.Kernel([5,0,0,65])] 
        expected_save = [remok.Kernel([5,4,0,62]), remok.Kernel([5,4,0,65])]
        for k in expected_delete:
            kernel_set(k)
        for k in expected_save:
            kernel_set(k)
        # the following lines requires operator __eq__ into class Kernel in order to work
        # this is why Kernel class has operator __eq__ implemented even if not used
        # in script code
        assert sorted(to_save) == sorted(expected_save)
        assert sorted(to_delete) == sorted(expected_delete)



def test_final_run_full_script(tmp_path):
    kernel_remove = tmp_path / "kernel_remove"
    with mock.patch(
        "subprocess.check_output", return_value=(HERE / "test01.txt").read_bytes()
    ), mock.patch("remok.KERNEL_REMOVE_PATH", kernel_remove):
        assert remok.main() is None
    expected_value=(HERE / "test01_output.txt").read_bytes()
    assert kernel_remove.read_bytes() == expected_value



def test_final_scrambled_input(tmp_path):
    kernel_remove = tmp_path / "kernel_remove"
    with mock.patch(
        "subprocess.check_output", return_value=(HERE / "test02.txt").read_bytes()
    ), mock.patch("remok.KERNEL_REMOVE_PATH", kernel_remove):
        assert remok.main() is None
    expected_value=(HERE / "test01_output.txt").read_bytes()
    assert kernel_remove.read_bytes() == expected_value

