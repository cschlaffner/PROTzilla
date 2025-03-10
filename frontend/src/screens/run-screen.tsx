import { Navbar } from "./../components"
import { useNavigate } from "react-router-dom"

export const RunScreen: React.FC = () => {
    const navigate = useNavigate()

    return (
        <div>
            <Navbar
                allowRunEdit={true}
                title="New Run"
                onNavigateHome={() => navigate("/")}
                onOpenSettings={() => {}}
                onOpenHelp={() => {}}
            />

        </div>
    )
}