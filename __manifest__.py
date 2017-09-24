# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2017 Humanytek (<www.humanytek.com>).
#    Rubén Bravo <rubenred18@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': "Compromise Products",
    'summary': """
    """,
    'description': """
    """,
    'author': "Humanytek",
    'website': "http://www.humanytek.com",
    'category': 'Sales',
    'version': '1.0.0',
    'depends': ['sale', 'stock', 'mrp_sale_info', 'product_brand'],
    'data': [
            'security/ir.model.access.csv',
            'view/sale_view.xml',
            'view/product_compromise_view.xml',
            'wizard/compromise_view.xml',
    ],
    'demo': [
    ],
}
