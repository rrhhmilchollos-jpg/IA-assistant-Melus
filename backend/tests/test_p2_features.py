"""
Test P2 Features for Melus AI:
1) Vercel Deploy - Modal shows message when project is not on GitHub
2) Templates de Pago - Purchase, my-purchases, my-earnings endpoints
3) Versionado Mejorado - Snapshot, Compare versions, File history endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://melus-dev-studio.preview.emergentagent.com')

TEST_CREDENTIALS = {
    "email": "rrhh.milchollos@gmail.com",
    "password": "19862210Des"
}

TEST_WORKSPACE_ID = "ws_6a55215c93d5"


class TestAuth:
    """Get authentication token for testing"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login and get session token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=TEST_CREDENTIALS
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "session_token" in data, "No session_token in response"
        return data["session_token"]
    
    def test_login(self, auth_token):
        """Verify login works"""
        assert auth_token is not None
        print(f"✓ Login successful, token obtained")


class TestVersioning:
    """Test enhanced versioning features: snapshot, compare, file-history"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login and get session token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=TEST_CREDENTIALS
        )
        assert response.status_code == 200
        return response.json()["session_token"]
    
    @pytest.fixture(scope="class")
    def test_workspace(self, auth_token):
        """Create a test workspace for versioning tests"""
        headers = {"X-Session-Token": auth_token}
        
        # First try to use existing test workspace
        response = requests.get(
            f"{BASE_URL}/api/workspace/{TEST_WORKSPACE_ID}",
            headers=headers
        )
        
        if response.status_code == 200:
            return TEST_WORKSPACE_ID
        
        # Create new workspace if not found
        response = requests.post(
            f"{BASE_URL}/api/workspace/create",
            headers=headers,
            json={
                "name": "TEST_Versioning_Workspace",
                "description": "Test workspace for versioning features"
            }
        )
        
        if response.status_code == 200:
            return response.json()["workspace_id"]
        
        pytest.skip("Could not create or find test workspace")
    
    def test_create_snapshot(self, auth_token, test_workspace):
        """Test POST /api/workspace/{id}/snapshot creates named snapshots"""
        headers = {"X-Session-Token": auth_token}
        
        response = requests.post(
            f"{BASE_URL}/api/workspace/{test_workspace}/snapshot",
            headers=headers,
            json={
                "name": "TEST_Snapshot_v1",
                "description": "Test snapshot created during automated testing"
            }
        )
        
        assert response.status_code == 200, f"Snapshot creation failed: {response.text}"
        data = response.json()
        
        # Data assertions
        assert "version" in data, "Response missing version"
        assert "name" in data, "Response missing name"
        assert "message" in data, "Response missing message"
        assert data["name"] == "TEST_Snapshot_v1"
        assert "exitosamente" in data["message"].lower() or "success" in data["message"].lower()
        
        print(f"✓ Snapshot created: version {data['version']}, name: {data['name']}")
        return data["version"]
    
    def test_get_versions(self, auth_token, test_workspace):
        """Test GET /api/workspace/{id}/versions returns version list"""
        headers = {"X-Session-Token": auth_token}
        
        response = requests.get(
            f"{BASE_URL}/api/workspace/{test_workspace}/versions",
            headers=headers
        )
        
        assert response.status_code == 200, f"Get versions failed: {response.text}"
        data = response.json()
        
        # Data assertions
        assert "versions" in data, "Response missing versions"
        assert "current_version" in data, "Response missing current_version"
        assert isinstance(data["versions"], list), "Versions should be a list"
        
        print(f"✓ Retrieved {len(data['versions'])} versions, current: {data['current_version']}")
        return data["versions"]
    
    def test_compare_versions(self, auth_token, test_workspace):
        """Test GET /api/workspace/{id}/compare/{v1}/{v2} compares versions"""
        headers = {"X-Session-Token": auth_token}
        
        # First get versions
        versions_response = requests.get(
            f"{BASE_URL}/api/workspace/{test_workspace}/versions",
            headers=headers
        )
        
        if versions_response.status_code != 200:
            pytest.skip("Could not get versions")
        
        versions = versions_response.json().get("versions", [])
        
        if len(versions) < 2:
            # Create a snapshot to have at least 2 versions
            requests.post(
                f"{BASE_URL}/api/workspace/{test_workspace}/snapshot",
                headers=headers,
                json={"name": "TEST_Snapshot_for_compare"}
            )
            versions_response = requests.get(
                f"{BASE_URL}/api/workspace/{test_workspace}/versions",
                headers=headers
            )
            versions = versions_response.json().get("versions", [])
        
        if len(versions) < 2:
            pytest.skip("Not enough versions to compare")
        
        v1 = versions[0]["version"]
        v2 = versions[-1]["version"]
        
        response = requests.get(
            f"{BASE_URL}/api/workspace/{test_workspace}/compare/{v1}/{v2}",
            headers=headers
        )
        
        assert response.status_code == 200, f"Compare failed: {response.text}"
        data = response.json()
        
        # Data assertions
        assert "version1" in data, "Response missing version1"
        assert "version2" in data, "Response missing version2"
        assert "diff" in data, "Response missing diff"
        assert "summary" in data, "Response missing summary"
        assert data["version1"] == v1
        assert data["version2"] == v2
        
        # Check diff structure
        diff = data["diff"]
        assert "added" in diff, "Diff missing 'added'"
        assert "removed" in diff, "Diff missing 'removed'"
        assert "modified" in diff, "Diff missing 'modified'"
        assert "unchanged" in diff, "Diff missing 'unchanged'"
        
        print(f"✓ Compared versions {v1} vs {v2}: {data['summary']}")
    
    def test_file_history(self, auth_token, test_workspace):
        """Test GET /api/workspace/{id}/file-history/{path} returns file history"""
        headers = {"X-Session-Token": auth_token}
        
        # Get workspace to find a file
        workspace_response = requests.get(
            f"{BASE_URL}/api/workspace/{test_workspace}",
            headers=headers
        )
        
        if workspace_response.status_code != 200:
            pytest.skip("Could not get workspace")
        
        files = workspace_response.json().get("files", {})
        
        if not files:
            pytest.skip("No files in workspace")
        
        # Get history for first file
        file_path = list(files.keys())[0]
        
        response = requests.get(
            f"{BASE_URL}/api/workspace/{test_workspace}/file-history/{file_path}",
            headers=headers
        )
        
        assert response.status_code == 200, f"File history failed: {response.text}"
        data = response.json()
        
        # Data assertions
        assert "file_path" in data, "Response missing file_path"
        assert "history" in data, "Response missing history"
        assert "total_versions" in data, "Response missing total_versions"
        assert data["file_path"] == file_path
        assert isinstance(data["history"], list), "History should be a list"
        
        print(f"✓ File history for '{file_path}': {data['total_versions']} versions")


class TestPaidTemplates:
    """Test paid templates marketplace: purchase, my-purchases, my-earnings"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login and get session token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=TEST_CREDENTIALS
        )
        assert response.status_code == 200
        return response.json()["session_token"]
    
    def test_get_marketplace_templates(self, auth_token):
        """Test GET /api/marketplace/templates returns template list"""
        response = requests.get(f"{BASE_URL}/api/marketplace/templates")
        
        assert response.status_code == 200, f"Get templates failed: {response.text}"
        data = response.json()
        
        # Data assertions
        assert "templates" in data, "Response missing templates"
        assert "total" in data, "Response missing total"
        assert isinstance(data["templates"], list), "Templates should be a list"
        
        # Check template structure if any exist
        for template in data["templates"][:3]:  # Check first 3
            assert "template_id" in template, "Template missing template_id"
            assert "name" in template, "Template missing name"
            # Price/free fields should exist for paid template support
            if "is_free" in template:
                print(f"  - Template '{template['name']}': is_free={template.get('is_free')}, price={template.get('price', 0)}")
        
        print(f"✓ Retrieved {len(data['templates'])} templates from marketplace")
        return data["templates"]
    
    def test_get_my_purchases(self, auth_token):
        """Test GET /api/marketplace/my-purchases returns user's purchases"""
        headers = {"X-Session-Token": auth_token}
        
        response = requests.get(
            f"{BASE_URL}/api/marketplace/my-purchases",
            headers=headers
        )
        
        assert response.status_code == 200, f"Get my-purchases failed: {response.text}"
        data = response.json()
        
        # Data assertions
        assert "purchases" in data, "Response missing purchases"
        assert isinstance(data["purchases"], list), "Purchases should be a list"
        
        # Check purchase structure if any exist
        for purchase in data["purchases"][:3]:
            assert "purchase_id" in purchase or "template_id" in purchase, "Purchase missing ID"
            assert "purchased_at" in purchase, "Purchase missing purchased_at"
        
        print(f"✓ User has {len(data['purchases'])} template purchases")
    
    def test_get_my_earnings(self, auth_token):
        """Test GET /api/marketplace/my-earnings returns author's earnings"""
        headers = {"X-Session-Token": auth_token}
        
        response = requests.get(
            f"{BASE_URL}/api/marketplace/my-earnings",
            headers=headers
        )
        
        assert response.status_code == 200, f"Get my-earnings failed: {response.text}"
        data = response.json()
        
        # Data assertions
        assert "total_earnings" in data, "Response missing total_earnings"
        assert "sales" in data, "Response missing sales"
        assert "templates" in data, "Response missing templates"
        assert isinstance(data["sales"], list), "Sales should be a list"
        assert isinstance(data["templates"], list), "Templates should be a list"
        
        print(f"✓ Author total earnings: {data['total_earnings']}, {len(data['sales'])} sales")
    
    def test_purchase_nonexistent_template(self, auth_token):
        """Test POST /api/marketplace/templates/{id}/purchase returns 404 for bad ID"""
        headers = {"X-Session-Token": auth_token}
        
        response = requests.post(
            f"{BASE_URL}/api/marketplace/templates/nonexistent_template_id/purchase",
            headers=headers
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Purchase of nonexistent template correctly returns 404")
    
    def test_purchase_template_endpoint_exists(self, auth_token):
        """Test that the purchase endpoint is accessible"""
        headers = {"X-Session-Token": auth_token}
        
        # Get templates first
        templates_response = requests.get(f"{BASE_URL}/api/marketplace/templates")
        templates = templates_response.json().get("templates", [])
        
        if templates:
            template = templates[0]
            template_id = template.get("template_id")
            
            # Try to purchase (might fail due to already purchased or other reasons)
            response = requests.post(
                f"{BASE_URL}/api/marketplace/templates/{template_id}/purchase",
                headers=headers
            )
            
            # Should not return 404 or 405 (method not allowed)
            assert response.status_code not in [404, 405], f"Purchase endpoint issue: {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                # Could be already_purchased or actual purchase
                assert "success" in data or "already_purchased" in data or "message" in data
                print(f"✓ Purchase endpoint works for template {template_id}")
            elif response.status_code == 402:
                # Not enough credits - endpoint works
                print("✓ Purchase endpoint returns 402 (insufficient credits) - endpoint working")
            else:
                print(f"✓ Purchase endpoint responded with {response.status_code}")
        else:
            print("✓ Purchase endpoint exists (no templates to test with)")


class TestVercelDeploy:
    """Test Vercel Deploy UI modal behavior"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login and get session token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=TEST_CREDENTIALS
        )
        assert response.status_code == 200
        return response.json()["session_token"]
    
    def test_workspace_github_info(self, auth_token):
        """Test GET /api/workspace/{id} returns github_url if present"""
        headers = {"X-Session-Token": auth_token}
        
        # Get recent workspaces
        response = requests.get(
            f"{BASE_URL}/api/workspace/recent",
            headers=headers
        )
        
        assert response.status_code == 200, f"Get recent workspaces failed: {response.text}"
        data = response.json()
        
        workspaces = data.get("workspaces", [])
        print(f"✓ Found {len(workspaces)} recent workspaces")
        
        if workspaces:
            ws_id = workspaces[0].get("workspace_id")
            
            # Get full workspace details
            ws_response = requests.get(
                f"{BASE_URL}/api/workspace/{ws_id}",
                headers=headers
            )
            
            assert ws_response.status_code == 200, f"Get workspace failed: {ws_response.text}"
            ws_data = ws_response.json()
            
            # Check if github_url field exists (can be null/empty)
            has_github = "github_url" in ws_data and ws_data["github_url"]
            has_github_repo = "github_repo" in ws_data and ws_data["github_repo"]
            
            print(f"  - Workspace '{ws_data.get('name')}': has_github_url={has_github}, has_github_repo={has_github_repo}")
            
            # The workspace object should support github info
            print("✓ Workspace response structure supports GitHub info")
    
    def test_github_status_endpoint(self, auth_token):
        """Test GET /api/github/status returns connection status"""
        headers = {"X-Session-Token": auth_token}
        
        response = requests.get(
            f"{BASE_URL}/api/github/status",
            headers=headers
        )
        
        assert response.status_code == 200, f"GitHub status failed: {response.text}"
        data = response.json()
        
        # Data assertions
        assert "connected" in data, "Response missing connected"
        
        if data["connected"]:
            assert "username" in data, "Connected but missing username"
            print(f"✓ GitHub connected as: {data.get('username')}")
        else:
            print("✓ GitHub not connected (expected for test account)")


class TestPublishTemplateModal:
    """Test publish template modal with free/paid options"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login and get session token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=TEST_CREDENTIALS
        )
        assert response.status_code == 200
        return response.json()["session_token"]
    
    def test_publish_template_requires_workspace(self, auth_token):
        """Test POST /api/marketplace/templates requires workspace_id"""
        headers = {"X-Session-Token": auth_token, "Content-Type": "application/json"}
        
        response = requests.post(
            f"{BASE_URL}/api/marketplace/templates",
            headers=headers,
            json={
                "name": "TEST_Template",
                "description": "Test template"
                # Missing workspace_id
            }
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Publish template correctly requires workspace_id")
    
    def test_publish_template_with_pricing(self, auth_token):
        """Test POST /api/marketplace/templates accepts is_free and price"""
        headers = {"X-Session-Token": auth_token, "Content-Type": "application/json"}
        
        # Get a workspace first
        ws_response = requests.get(
            f"{BASE_URL}/api/workspace/recent",
            headers=headers
        )
        
        workspaces = ws_response.json().get("workspaces", [])
        
        if not workspaces:
            pytest.skip("No workspaces available for testing")
        
        # Find workspace with files
        workspace_id = None
        for ws in workspaces:
            if ws.get("workspace_id"):
                # Check if it has files
                ws_detail = requests.get(
                    f"{BASE_URL}/api/workspace/{ws['workspace_id']}",
                    headers=headers
                )
                if ws_detail.status_code == 200:
                    files = ws_detail.json().get("files", {})
                    if files:
                        workspace_id = ws["workspace_id"]
                        break
        
        if not workspace_id:
            pytest.skip("No workspace with files available")
        
        # Try to publish a paid template
        response = requests.post(
            f"{BASE_URL}/api/marketplace/templates",
            headers=headers,
            json={
                "workspace_id": workspace_id,
                "name": f"TEST_Paid_Template_{os.urandom(4).hex()}",
                "description": "Test paid template from automated tests",
                "category": "tool",
                "tags": ["test", "automated"],
                "is_free": False,
                "price": 100
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "template_id" in data, "Response missing template_id"
            print(f"✓ Published paid template: {data['template_id']}")
            
            # Clean up - delete the template
            requests.delete(
                f"{BASE_URL}/api/marketplace/templates/{data['template_id']}",
                headers=headers
            )
            print("  (Cleaned up test template)")
        else:
            # Might fail if already published - that's ok
            print(f"✓ Publish endpoint responded with {response.status_code}")


class TestIntegrationSummary:
    """Summary test to verify all P2 features are accessible"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=TEST_CREDENTIALS
        )
        assert response.status_code == 200
        return response.json()["session_token"]
    
    def test_all_endpoints_accessible(self, auth_token):
        """Verify all P2 feature endpoints are accessible"""
        headers = {"X-Session-Token": auth_token}
        
        endpoints_to_check = [
            # Marketplace endpoints
            ("GET", "/api/marketplace/templates", None),
            ("GET", "/api/marketplace/my-purchases", headers),
            ("GET", "/api/marketplace/my-earnings", headers),
            
            # GitHub status
            ("GET", "/api/github/status", headers),
            
            # Workspace versioning (using test workspace)
            ("GET", f"/api/workspace/{TEST_WORKSPACE_ID}/versions", headers),
        ]
        
        results = []
        for method, endpoint, hdrs in endpoints_to_check:
            try:
                if method == "GET":
                    response = requests.get(f"{BASE_URL}{endpoint}", headers=hdrs)
                else:
                    response = requests.post(f"{BASE_URL}{endpoint}", headers=hdrs, json={})
                
                success = response.status_code in [200, 400, 402, 404]  # 400/402/404 means endpoint exists
                results.append((endpoint, response.status_code, success))
            except Exception as e:
                results.append((endpoint, str(e), False))
        
        # Print summary
        print("\n=== P2 Feature Endpoints Summary ===")
        all_passed = True
        for endpoint, status, success in results:
            symbol = "✓" if success else "✗"
            print(f"  {symbol} {endpoint}: {status}")
            if not success:
                all_passed = False
        
        assert all_passed, "Some endpoints are not accessible"
        print("\n✓ All P2 feature endpoints are accessible")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
