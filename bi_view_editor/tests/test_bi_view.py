# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestBiViewEditor(common.TransactionCase):

    def setUp(self):

        def _get_models(model_name_list):
            Model = self.env['ir.model']
            return (Model.search(
                [('model', '=', name)]) for name in model_name_list)

        def _get_fields(model_field_list):
            ModelFields = self.env['ir.model.fields']
            return (ModelFields.search(
                [('model', '=', model_field[0]),
                 ('name', '=', model_field[1])],
                limit=1) for model_field in model_field_list)

        super(TestBiViewEditor, self).setUp()
        self.partner_model_name = 'res.partner'
        self.partner_field_name = 'name'
        self.partner_company_field_name = 'company_id'
        self.company_model_name = 'res.company'
        self.company_field_name = 'name'

        self.bi_view1 = None

        self.partner_model, self.company_model = _get_models(
            [self.partner_model_name, self.company_model_name])

        (self.partner_field,
         self.partner_company_field,
         self.company_field) = _get_fields([
             (self.partner_model_name, self.partner_field_name),
             (self.partner_model_name, self.partner_company_field_name),
             (self.company_model_name, self.company_field_name)])

        data = [
            {'model_id': self.partner_model.id,
             'name': self.partner_field_name,
             'model_name': self.partner_model.name,
             'model': self.partner_model_name,
             'custom': 0,
             'type': self.partner_field.ttype,
             'id': self.partner_field.id,
             'description': self.partner_field.field_description,
             'table_alias': 't0',
             'row': 0,
             'column': 1,
             'measure': 0
             },
            {'model_id': self.partner_model.id,
             'name': self.partner_company_field_name,
             'table_alias': 't0',
             'custom': 0,
             'relation': self.company_model_name,
             'model': self.partner_model_name,
             'model_name': self.partner_model.name,
             'type': self.partner_company_field.ttype,
             'id': self.partner_company_field.id,
             'join_node': 't1',
             'description': self.partner_company_field.field_description,
             'row': 0,
             'column': 0,
             'measure': 0
             },
            {'model_id': self.company_model.id,
             'name': 'name_1',
             'model_name': self.company_model.name,
             'model': self.company_model_name,
             'custom': 0,
             'type': self.company_field.ttype,
             'id': self.company_field.id,
             'description': self.company_field.field_description,
             'table_alias': 't1',
             'row': 1,
             'column': 0,
             'measure': 0
             }
        ]
        format_data = self.env['bve.view']._get_format_data(str(data))

        self.bi_view1_vals = {
            'state': 'draft',
            'data': format_data
        }

    def test_01_setup(self):
        self.assertIsNotNone(self.partner_model)
        self.assertIsNotNone(self.company_model)
        self.assertIsNotNone(self.partner_field)
        self.assertIsNotNone(self.partner_company_field)
        self.assertIsNotNone(self.company_field)

    def test_02_get_fields(self):
        Model = self.env['ir.model']
        fields = Model.get_fields(self.partner_model.id)
        self.assertIsInstance(fields, list)
        self.assertGreater(len(fields), 0)

    def test_03_get_join_nodes(self):
        new_field = {
            'model_id': self.partner_model.id,
            'name': self.partner_field_name,
            'custom': False,
            'id': self.partner_field.id,
            'model': self.partner_model_name,
            'type': self.partner_field.ttype,
            'model_name': self.partner_model.name,
            'description': self.partner_field.field_description
        }
        Model = self.env['ir.model']
        nodes = Model.get_join_nodes([], new_field)
        self.assertIsInstance(nodes, list)
        self.assertEqual(len(nodes), 0)

    def test_04_get_related_models(self):
        Model = self.env['ir.model']
        related_models = Model.get_related_models({
            't0': self.partner_model.id,
            't1': self.company_model.id
        })
        self.assertIsInstance(related_models, list)
        self.assertGreater(len(related_models), 0)

    def test_05_create_copy_view(self):
        vals = self.bi_view1_vals
        vals.update({'name': 'Test View1'})

        # create
        bi_view1 = self.env['bve.view'].create(vals)
        self.assertIsNotNone(bi_view1)
        self.assertEqual(len(bi_view1), 1)
        self.assertEqual(bi_view1.state, 'draft')

        # copy
        bi_view2 = bi_view1.copy()
        self.assertEqual(bi_view2.name, 'Test View1 (copy)')

    def test_06_create_group_bve_object(self):
        vals = self.bi_view1_vals
        employees_group = self.env.ref('base.group_user')
        vals.update({
            'name': 'Test View2',
            'group_ids': [(6, 0, [employees_group.id])],
        })

        bi_view2 = self.env['bve.view'].create(vals)
        self.assertEqual(len(bi_view2.user_ids), len(employees_group.users))

    def test_07_create_open_bve_object(self):
        vals = self.bi_view1_vals
        employees_group = self.env.ref('base.group_user')
        vals.update({
            'name': 'Test View3',
            'group_ids': [(6, 0, [employees_group.id])],
        })
        bi_view3 = self.env['bve.view'].create(vals)
        self.assertEqual(len(bi_view3), 1)

        # create bve object
        # bi_view3.action_create()
        # model = self.env['ir.model'].search([
        #     ('model', '=', 'x_bve.testview3'),
        #     ('name', '=', 'Test View3')
        # ])
        # self.assertEqual(len(model), 1)
        #
        # # open view
        # open_action = bi_view3.open_view()
        # self.assertEqual(isinstance(open_action, dict), True)
        #
        # # open view
        # bi_view3.action_reset()
        # bi_view3.unlink()
