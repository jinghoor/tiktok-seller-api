"""自动生成,勿手改。源: spec/endpoints.json (extract_endpoints.py)。"""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..transport import Transport


class AutomationAPI:
    """自动化 automation-v1.aiadfly.com —— 策略/标签/素材池/广告列表"""

    BACKENDS = ('automation',)
    _GROUP_DEFAULT = 'automation'

    def __init__(self, t: Transport):
        self._t = t

    def get_adgroup_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /adgroup/list  (前端 getAdgroupListAPI)"""
        return self._t.post('automation', "/adgroup/list", body, **kw)

    def get_advertiser_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/list  (前端 getAdvertiserListAPI$1)"""
        return self._t.post('automation', "/advertiser/list", body, **kw)

    def bind_label_relation(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser_label_relation/bind  (前端 bindLabelRelationAPI)"""
        return self._t.post('automation', "/advertiser_label_relation/bind", body, **kw)

    def get_label_relation_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser_label_relation/find  (前端 getLabelRelationListAPI)"""
        return self._t.post('automation', "/advertiser_label_relation/find", body, **kw)

    def unbind_label_relation(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser_label_relation/unbind  (前端 unbindLabelRelationAPI)"""
        return self._t.post('automation', "/advertiser_label_relation/unbind", body, **kw)

    def get_campaign_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /campaign/list  (前端 getCampaignListAPI$1)"""
        return self._t.post('automation', "/campaign/list", body, **kw)

    def add_label(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /label/add  (前端 addLabelAPI)"""
        return self._t.post('automation', "/label/add", body, **kw)

    def delete_label(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /label/del  (前端 deleteLabelAPI)"""
        return self._t.post('automation', "/label/del", body, **kw)

    def get_label_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /label/list  (前端 getLabelListAPI)"""
        return self._t.post('automation', "/label/list", body, **kw)

    def add_label_category(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /label_category/add  (前端 addLabelCategoryAPI)"""
        return self._t.post('automation', "/label_category/add", body, **kw)

    def delete_label_category(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /label_category/del  (前端 deleteLabelCategoryAPI)"""
        return self._t.post('automation', "/label_category/del", body, **kw)

    def get_label_category_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /label_category/list  (前端 getLabelCategoryListAPI)"""
        return self._t.post('automation', "/label_category/list", body, **kw)

    def get_gmvmax_material_daily_data(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /material/daily  (前端 getGmvmaxMaterialDailyDataAPI)"""
        return self._t.post('automation', "/material/daily", body, **kw)

    def export_gmvmax_materials(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /material/export  (前端 exportGmvmaxMaterialsAPI)"""
        return self._t.post('automation', "/material/export", body, **kw)

    def get_material_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /material/list  (前端 getMaterialListAPI)"""
        return self._t.post('automation', "/material/list", body, **kw)

    def get_gmvmax_material_summary(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /material/summary  (前端 getGmvmaxMaterialSummaryAPI)"""
        return self._t.post('automation', "/material/summary", body, **kw)

    def add_material_group(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /material_group/add  (前端 addMaterialGroupAPI)"""
        return self._t.post('automation', "/material_group/add", body, **kw)

    def delete_material_group(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /material_group/del  (前端 deleteMaterialGroupAPI)"""
        return self._t.post('automation', "/material_group/del", body, **kw)

    def get_material_grou_detail(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /material_group/detail  (前端 getMaterialGrouDetailAPI)"""
        return self._t.post('automation', "/material_group/detail", body, **kw)

    def edit_material_group(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /material_group/edit  (前端 editMaterialGroupAPI)"""
        return self._t.post('automation', "/material_group/edit", body, **kw)

    def get_material_group_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /material_group/list  (前端 getMaterialGroupListAPI)"""
        return self._t.post('automation', "/material_group/list", body, **kw)

    def automation_add_tactic(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tactic/add  (前端 automationAddTacticAPI)"""
        return self._t.post('automation', "/tactic/add", body, **kw)

    def automationg_get_tactic_adv_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tactic/adv/list  (前端 automationgGetTacticAdvListAPI)
        实测必需字段(1 个,字段已摸清): tactic_ex_id:string
        可用 body 样例: {"page": 1, "page_size": 5, "tactic_ex_id": "7689XXXXXXXXXX05"}
        """
        return self._t.post('automation', "/tactic/adv/list", body, **kw)

    def automation_bind_tactic(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tactic/bind  (前端 automationBindTacticAPI)"""
        return self._t.post('automation', "/tactic/bind", body, **kw)

    def automation_delete_tactic(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tactic/delete  (前端 automationDeleteTacticAPI)"""
        return self._t.post('automation', "/tactic/delete", body, **kw)

    def automation_edit_tactic(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tactic/edit  (前端 automationEditTacticAPI)"""
        return self._t.post('automation', "/tactic/edit", body, **kw)

    def automation_find_tactic(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tactic/find  (前端 automationFindTacticAPI)
        实测必需字段(1 个,字段已摸清): tactic_ex_id:string
        可用 body 样例: {"page": 1, "page_size": 5, "tactic_ex_id": "7689XXXXXXXXXX05"}
        """
        return self._t.post('automation', "/tactic/find", body, **kw)

    def automation_get_list_tactic(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tactic/list  (前端 automationGetListTacticAPI)"""
        return self._t.post('automation', "/tactic/list", body, **kw)

    def automation_update_tactic_status(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tactic/status/update  (前端 automationUpdateTacticStatusAPI)"""
        return self._t.post('automation', "/tactic/status/update", body, **kw)

    def automation_un_bind_tactic(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tactic/unbind  (前端 automationUnBindTacticAPI)"""
        return self._t.post('automation', "/tactic/unbind", body, **kw)

    def tactic_action_logs_export(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tactic_action_log/export  (前端 tacticActionLogsExportAPI)"""
        return self._t.post('automation', "/tactic_action_log/export", body, **kw)

    def tactic_action_logs(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tactic_action_log/list  (前端 tacticActionLogsAPI)"""
        return self._t.post('automation', "/tactic_action_log/list", body, **kw)

    def tactic_logs_export(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tactic_change_log/export  (前端 tacticLogsExportAPI)"""
        return self._t.post('automation', "/tactic_change_log/export", body, **kw)

    def tactic_logs(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tactic_change_log/list  (前端 tacticLogsAPI)"""
        return self._t.post('automation', "/tactic_change_log/list", body, **kw)

    def call(self, method: str, path: str, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """任意路径逃生口:call("POST", "/tiktok/gmv_max/list", {...})。"""
        return self._t.request(method.upper(), path, json_body=body, group=self._GROUP_DEFAULT, **kw)
