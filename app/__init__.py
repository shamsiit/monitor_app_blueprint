from flask import Flask
import os

from app.module_cpu.controllers import mod_cpu
from app.module_mem.controllers import mod_mem
from app.module_net.controllers import mod_net
from app.module_diskio.controllers import mod_diskio
from app.module_disk.controllers import mod_disk
from app.module_kernel.controllers import mod_kernel
from app.module_netstat.controllers import mod_netstat
from app.module_processes.controllers import mod_processes
from app.module_swap.controllers import mod_swap
from app.module_system.controllers import mod_system
from app.module_main.controllers import mod_main
from app.module_role.controllers import mod_role
from app.module_user.controllers import mod_user

app = Flask(__name__)

secret_key = os.urandom(24)

# Register blueprint(s)
app.register_blueprint(mod_cpu)
app.register_blueprint(mod_mem)
app.register_blueprint(mod_net)
app.register_blueprint(mod_diskio)
app.register_blueprint(mod_disk)
app.register_blueprint(mod_kernel)
app.register_blueprint(mod_netstat)
app.register_blueprint(mod_processes)
app.register_blueprint(mod_swap)
app.register_blueprint(mod_system)
app.register_blueprint(mod_main)
app.register_blueprint(mod_role)
app.register_blueprint(mod_user)

app.secret_key = secret_key
